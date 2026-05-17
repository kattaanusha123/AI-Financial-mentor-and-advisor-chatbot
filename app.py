"""
Main Flask Application
Financial Mentor and Advisor Chatbot API
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os

# Use package-style imports so the editor (Pylance) can resolve modules when workspace root is project root
from backend.config import Config
from backend.models import db, User, ChatHistory
from backend.nlp_processor import NLPProcessor
from backend.financial_calculator import FinancialCalculator
from backend.market_updates import MarketUpdates
from backend.translator import Translator

app = Flask(__name__)
app.config.from_object(Config)

# Serve frontend static files (so opening http://127.0.0.1:5000/ shows the UI instead of a directory listing)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    # If the requested path exists in frontend, serve it; otherwise fall back to index.html
    full_path = os.path.join(frontend_dir, path)
    if path and os.path.exists(full_path) and os.path.isfile(full_path):
        # send file relative to frontend directory
        return send_from_directory(frontend_dir, path)
    return send_from_directory(frontend_dir, 'index.html')

# Configure JWT - use SECRET_KEY as JWT_SECRET_KEY if not explicitly set
if not app.config.get('JWT_SECRET_KEY'):
    app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Ensure JWT_SECRET_KEY matches SECRET_KEY
app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure JWT token location
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

CORS(app)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"JWT Invalid Token Error: {str(error)}")
    print(f"JWT_SECRET_KEY set: {bool(app.config.get('JWT_SECRET_KEY'))}")
    print(f"SECRET_KEY set: {bool(app.config.get('SECRET_KEY'))}")
    return jsonify({'error': 'Invalid or expired token. Please login again.'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization token is required'}), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Fresh token required'}), 401

# Initialize processors
nlp_processor = NLPProcessor()
financial_calculator = FinancialCalculator()
market_updates = MarketUpdates()
translator = Translator()

# Create database tables
with app.app_context():
    db.create_all()

# Routes

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate access token
        try:
            access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=30))
            print(f"Token created for user_id: {user.id}")
        except Exception as token_error:
            print(f"Token creation error: {str(token_error)}")
            return jsonify({'error': 'Failed to create authentication token'}), 500
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Generate access token
        try:
            access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=30))
            print(f"Token created for user_id: {user.id}")
        except Exception as token_error:
            print(f"Token creation error: {str(token_error)}")
            return jsonify({'error': 'Failed to create authentication token'}), 500
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({'error': 'Invalid token - no user ID'}), 401
            
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
    
    except Exception as e:
        print(f"Get User Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/user/language', methods=['PUT'])
@jwt_required()
def update_language():
    """Update user's preferred language"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        language = data.get('language', 'en')
        
        # Validate language code
        valid_languages = ['en', 'hi', 'te', 'ta', 'mr', 'gu', 'kn', 'ml', 'pa', 'bn', 'or', 'as']
        if language not in valid_languages:
            return jsonify({'error': 'Invalid language code'}), 400
        
        user.preferred_language = language
        db.session.commit()
        
        return jsonify({
            'message': 'Language preference updated',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-history', methods=['GET'])
@jwt_required()
def export_history():
    """Export chat history as text"""
    try:
        user_id = get_jwt_identity()
        user_id = int(user_id) if user_id else None
        
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        history = ChatHistory.query.filter_by(user_id=user_id)\
            .order_by(ChatHistory.timestamp.desc())\
            .all()
        
        # Generate export text
        export_text = f"Chat History Export\n"
        export_text += f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += f"{'='*50}\n\n"
        
        for entry in history:
            date = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S') if entry.timestamp else 'N/A'
            export_text += f"[{date}]\n"
            export_text += f"You: {entry.query}\n"
            export_text += f"Bot: {entry.response}\n"
            export_text += f"{'-'*50}\n\n"
        
        return jsonify({
            'export': export_text,
            'filename': f'chat_history_{datetime.utcnow().strftime("%Y%m%d")}.txt'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint - process user queries (supports guest mode)"""
    try:
        # Check if user is authenticated (optional for guest mode)
        user_id = None
        user = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from flask_jwt_extended import verify_jwt_in_request
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                if user_id:
                    user = User.query.get(user_id)
            except:
                # Invalid token or no token - continue as guest
                pass
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Determine language preference: priority -> explicit request body language -> authenticated user's preference -> detected language -> default 'en'
        query_lang = translator.detect_language(query)
        requested_lang = data.get('language') if isinstance(data, dict) else None
        if user:
            user_lang = user.preferred_language or requested_lang or query_lang or 'en'
        else:
            # Guest mode - use requested language (from UI) if provided, otherwise detect from query
            user_lang = requested_lang or (query_lang if query_lang in ['en', 'hi', 'te', 'mr'] else 'en')
        
        # Handle greeting with proper language first
        if nlp_processor.is_greeting(query):
            response_text = translator.get_greeting(user_lang)
            # Save to history only if user is authenticated
            if user_id:
                chat_history = ChatHistory(
                    user_id=user_id,
                    query=query,
                    response=response_text
                )
                db.session.add(chat_history)
                db.session.commit()
            
            return jsonify({
                'response': response_text,
                'type': 'greeting',
                'language': user_lang
            })
        
        # Fetch recent user history for personalization if authenticated
        user_history = None
        try:
            if user_id:
                # ensure integer id for DB lookup
                try:
                    uid = int(user_id)
                except Exception:
                    uid = None
                if uid:
                    recent = ChatHistory.query.filter_by(user_id=uid).order_by(ChatHistory.timestamp.desc()).limit(50).all()
                    # Pass a list of dicts with query/response for NLP processing
                    user_history = []
                    for e in recent:
                        try:
                            user_history.append({'query': e.query, 'response': e.response})
                        except Exception:
                            continue

        except Exception as hist_err:
            print(f"Failed to fetch user history for personalization: {str(hist_err)}")

        # Do not accept guest history from frontend; keep previous behavior where only authenticated
        # users have history pulled from the database for personalization. Guest-side history remains
        # in localStorage and is not sent to the server.

        # Process query using NLP (pass user_history if available)
        nlp_response = nlp_processor.process_query(query, user_history=user_history)
        
        response_text = nlp_response['message']
        
        # Translate response if user prefers different language
        suggested_term = nlp_response.get('suggested_term')
        if user_lang != 'en':
            response_text = translator.translate_response(response_text, user_lang, term=suggested_term)
        
        # If calculation is required, try to extract parameters
        if nlp_response['requires_calculation'] and nlp_response['calculation_type']:
            numbers = nlp_processor.extract_numbers(query)
            calc_type = nlp_response['calculation_type']
            
            try:
                if calc_type == 'emi':
                    if len(numbers) >= 3:
                        result = financial_calculator.calculate_emi(
                            principal=numbers[0],
                            rate=numbers[1],
                            tenure_months=int(numbers[2])
                        )
                        # Translate calculation labels
                        if user_lang == 'hi':
                            response_text += f"\n\nगणना परिणाम:\n"
                            response_text += f"ईएमआई: ₹{result['emi']:.2f}\n"
                            response_text += f"कुल भुगतान: ₹{result['total_payment']:.2f}\n"
                            response_text += f"कुल ब्याज: ₹{result['total_interest']:.2f}"
                        elif user_lang == 'te':
                            response_text += f"\n\nలెక్కల ఫలితాలు:\n"
                            response_text += f"ఇఎమ్ఐ: ₹{result['emi']:.2f}\n"
                            response_text += f"మొత్తం చెల్లింపు: ₹{result['total_payment']:.2f}\n"
                            response_text += f"మొత్తం వడ్డీ: ₹{result['total_interest']:.2f}"
                        elif user_lang == 'mr':
                            response_text += f"\n\nगणना परिणाम:\n"
                            response_text += f"EMI: ₹{result['emi']:.2f}\n"
                            response_text += f"एकूण देय: ₹{result['total_payment']:.2f}\n"
                            response_text += f"एकूण व्याज: ₹{result['total_interest']:.2f}"
                        else:
                            response_text += f"\n\nCalculation Results:\n"
                            response_text += f"EMI: ₹{result['emi']:.2f}\n"
                            response_text += f"Total Payment: ₹{result['total_payment']:.2f}\n"
                            response_text += f"Total Interest: ₹{result['total_interest']:.2f}"
                
                elif calc_type == 'sip':
                    if len(numbers) >= 3:
                        result = financial_calculator.calculate_sip(
                            monthly_investment=numbers[0],
                            rate=numbers[1],
                            time_years=int(numbers[2])
                        )
                        # Translate calculation labels
                        if user_lang == 'hi':
                            response_text += f"\n\nगणना परिणाम:\n"
                            response_text += f"कुल निवेश: ₹{result['total_invested']:.2f}\n"
                            response_text += f"परिपक्वता राशि: ₹{result['maturity_amount']:.2f}\n"
                            response_text += f"लाभ: ₹{result['gains']:.2f}\n"
                            response_text += f"रिटर्न: {result['return_percentage']:.2f}%"
                        elif user_lang == 'te':
                            response_text += f"\n\nలెక్కల ఫలితాలు:\n"
                            response_text += f"మొత్తం పెట్టుబడి: ₹{result['total_invested']:.2f}\n"
                            response_text += f"మెచ్యోరిటీ మొత్తం: ₹{result['maturity_amount']:.2f}\n"
                            response_text += f"లాభాలు: ₹{result['gains']:.2f}\n"
                            response_text += f"రాబడి: {result['return_percentage']:.2f}%"
                        elif user_lang == 'mr':
                            response_text += f"\n\nगणना परिणाम:\n"
                            response_text += f"एकूण गुंतवणूक: ₹{result['total_invested']:.2f}\n"
                            response_text += f"परिपक्वता रक्कम: ₹{result['maturity_amount']:.2f}\n"
                            response_text += f"नफा: ₹{result['gains']:.2f}\n"
                            response_text += f"परतावा: {result['return_percentage']:.2f}%"
                        else:
                            response_text += f"\n\nCalculation Results:\n"
                            response_text += f"Total Invested: ₹{result['total_invested']:.2f}\n"
                            response_text += f"Maturity Amount: ₹{result['maturity_amount']:.2f}\n"
                            response_text += f"Gains: ₹{result['gains']:.2f}\n"
                            response_text += f"Return: {result['return_percentage']:.2f}%"
                
                elif calc_type == 'compound_interest':
                    if len(numbers) >= 3:
                        result = financial_calculator.calculate_compound_interest(
                            principal=numbers[0],
                            rate=numbers[1],
                            time_years=int(numbers[2])
                        )
                        # Translate calculation labels
                        if user_lang == 'hi':
                            response_text += f"\n\nगणना परिणाम:\n"
                            response_text += f"परिपक्वता राशि: ₹{result['maturity_amount']:.2f}\n"
                            response_text += f"अर्जित ब्याज: ₹{result['interest_earned']:.2f}"
                        elif user_lang == 'te':
                            response_text += f"\n\nలెక్కల ఫలితాలు:\n"
                            response_text += f"మెచ్యోరిటీ మొత్తం: ₹{result['maturity_amount']:.2f}\n"
                            response_text += f"సంపాదించిన వడ్డీ: ₹{result['interest_earned']:.2f}"
                        elif user_lang == 'mr':
                            response_text += f"\n\nगणना परिणाम:\n"
                            response_text += f"परिपक्वता रक्कम: ₹{result['maturity_amount']:.2f}\n"
                            response_text += f"मिळवलेले व्याज: ₹{result['interest_earned']:.2f}"
                        else:
                            response_text += f"\n\nCalculation Results:\n"
                            response_text += f"Maturity Amount: ₹{result['maturity_amount']:.2f}\n"
                            response_text += f"Interest Earned: ₹{result['interest_earned']:.2f}"
                
                elif calc_type == 'simple_interest':
                    if len(numbers) >= 3:
                        result = financial_calculator.calculate_simple_interest(
                            principal=numbers[0],
                            rate=numbers[1],
                            time_years=int(numbers[2])
                        )
                        # Translate calculation labels
                        if user_lang == 'hi':
                            response_text += f"\n\nगणना परिणाम:\n"
                            response_text += f"कुल राशि: ₹{result['total_amount']:.2f}\n"
                            response_text += f"अर्जित ब्याज: ₹{result.get('interest_earned', result.get('interest', 0)):.2f}"
                        elif user_lang == 'te':
                            response_text += f"\n\nలెక్కల ఫలితాలు:\n"
                            response_text += f"మొత్తం మొత్తం: ₹{result['total_amount']:.2f}\n"
                            response_text += f"సంపాదించిన వడ్డీ: ₹{result.get('interest_earned', result.get('interest', 0)):.2f}"
                        elif user_lang == 'mr':
                            response_text += f"\n\nगणना परिणाम:\n"
                            response_text += f"एकूण रक्कम: ₹{result['total_amount']:.2f}\n"
                            response_text += f"मिळवलेले व्याज: ₹{result.get('interest_earned', result.get('interest', 0)):.2f}"
                        else:
                            response_text += f"\n\nCalculation Results:\n"
                            response_text += f"Total Amount: ₹{result['total_amount']:.2f}\n"
                            response_text += f"Interest: ₹{result.get('interest_earned', result.get('interest', 0)):.2f}"
                
            except Exception as calc_error:
                response_text += f"\n\nI had trouble calculating with those numbers. Please provide: principal amount, interest rate (%), and time period."
        
        # Save chat history only if user is authenticated
        if user_id:
            try:
                chat_history = ChatHistory(
                    user_id=user_id,
                    query=query,
                    response=response_text,
                    query_type=nlp_response['type']
                )
                db.session.add(chat_history)
                db.session.commit()
            except Exception as db_error:
                print(f"Database Error: {str(db_error)}")
                # Continue even if history save fails
        
        resp_payload = {
            'response': response_text,
            'type': nlp_response.get('type'),
            'calculation_type': nlp_response.get('calculation_type'),
            'timestamp': datetime.utcnow().isoformat()
        }
        # Include any NLP follow-up prompts or structured personalization data
        if isinstance(nlp_response, dict):
            if nlp_response.get('follow_up'):
                resp_payload['follow_up'] = True
                resp_payload['follow_up_question'] = nlp_response.get('follow_up_question')
            # Personalized allocation removed per user request; do not include structured allocation data
            # in the API response.

        return jsonify(resp_payload), 200
    
    except Exception as e:
        return jsonify({'error': 'Unable to process your request. Please try again.'}), 500

@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get user chat history"""
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({'error': 'Invalid token - no user ID'}), 401
        
        # Convert user_id to int if it's a string (JWT identity might be string)
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID format'}), 400
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        limit = request.args.get('limit', 50, type=int)
        
        # Safe query with proper error handling
        try:
            history = ChatHistory.query.filter_by(user_id=user_id)\
                .order_by(ChatHistory.timestamp.desc())\
                .limit(limit)\
                .all()
            
            # Convert to dict with error handling
            history_list = []
            for entry in history:
                try:
                    history_list.append(entry.to_dict())
                except Exception as entry_error:
                    print(f"Error converting history entry {entry.id}: {str(entry_error)}")
                    # Skip problematic entries but continue
                    continue
            
            return jsonify({
                'history': history_list
            }), 200
            
        except Exception as query_error:
            print(f"Database Query Error: {str(query_error)}")
            import traceback
            traceback.print_exc()
            # Return empty history instead of error
            return jsonify({
                'history': []
            }), 200
    
    except Exception as e:
        print(f"History Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Unable to fetch history: {str(e)}'}), 500


@app.route('/api/history/import', methods=['POST'])
@jwt_required()
def import_history():
    """Import guest history into authenticated user's history.
    Expects JSON body: { entries: [ { query, response, timestamp, type }, ... ] }
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Invalid token - no user ID'}), 401

        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json() or {}
        entries = data.get('entries') or []
        if not isinstance(entries, list) or not entries:
            return jsonify({'message': 'No entries to import', 'imported': 0}), 200

        imported = 0
        for e in entries:
            try:
                q = e.get('query')
                r = e.get('response')
                ts = e.get('timestamp')
                qtype = e.get('type')
                if not q or not r:
                    continue
                # Parse timestamp if provided
                try:
                    from dateutil import parser as dateparser
                    parsed_ts = dateparser.parse(ts) if ts else None
                except Exception:
                    parsed_ts = None

                chat_entry = ChatHistory(
                    user_id=int(user_id),
                    query=q,
                    response=r,
                    timestamp=parsed_ts if parsed_ts else datetime.utcnow(),
                    query_type=qtype
                )
                db.session.add(chat_entry)
                imported += 1
            except Exception as inner_e:
                print(f"Skipping entry due to error: {str(inner_e)}")

        if imported:
            db.session.commit()

        return jsonify({'message': 'Import complete', 'imported': imported}), 200

    except Exception as e:
        print(f"Import History Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to import history'}), 500

@app.route('/api/calculate', methods=['POST'])
@jwt_required()
def calculate():
    """Financial calculation endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        calc_type = data.get('type')
        
        if not calc_type:
            return jsonify({'error': 'Calculation type is required'}), 400
        
        if calc_type == 'emi':
            principal = data.get('principal')
            rate = data.get('rate')
            tenure = data.get('tenure_months')
            if not all([principal, rate, tenure]):
                return jsonify({'error': 'Principal, rate, and tenure_months are required'}), 400
            result = financial_calculator.calculate_emi(principal, rate, tenure)
        elif calc_type == 'sip':
            amount = data.get('monthly_investment')
            rate = data.get('rate')
            years = data.get('time_years')
            if not all([amount, rate, years]):
                return jsonify({'error': 'monthly_investment, rate, and time_years are required'}), 400
            result = financial_calculator.calculate_sip(amount, rate, years)
        elif calc_type == 'compound_interest':
            principal = data.get('principal')
            rate = data.get('rate')
            years = data.get('time_years')
            if not all([principal, rate, years]):
                return jsonify({'error': 'Principal, rate, and time_years are required'}), 400
            result = financial_calculator.calculate_compound_interest(principal, rate, years)
        elif calc_type == 'simple_interest':
            principal = data.get('principal')
            rate = data.get('rate')
            years = data.get('time_years')
            if not all([principal, rate, years]):
                return jsonify({'error': 'Principal, rate, and time_years are required'}), 400
            result = financial_calculator.calculate_simple_interest(principal, rate, years)
        elif calc_type == 'future_value':
            principal = data.get('principal')
            rate = data.get('rate')
            years = data.get('time_years')
            monthly_contrib = data.get('monthly_contribution', 0)
            if not all([principal is not None, rate is not None, years is not None]):
                return jsonify({'error': 'Principal, rate, and time_years are required'}), 400
            result = financial_calculator.calculate_future_value(principal, rate, years, monthly_contrib)
        else:
            return jsonify({'error': f'Invalid calculation type: {calc_type}'}), 400
        
        return jsonify({'result': result}), 200
    
    except Exception as e:
        return jsonify({'error': 'Calculation failed. Please check your inputs.'}), 500

@app.route('/api/market-updates', methods=['GET'])
@jwt_required()
def get_market_updates():
    """Get market updates"""
    try:
        summary = market_updates.get_market_summary()
        return jsonify(summary), 200
    except Exception as e:
        print(f"Market Updates Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Unable to fetch market updates'}), 500

@app.route('/api/charts', methods=['GET'])
@jwt_required()
def get_charts_data():
    """Get chart data for Bitcoin, Gold, and Stocks"""
    try:
        charts_data = market_updates.get_all_charts_data()
        return jsonify(charts_data), 200
    except Exception as e:
        print(f"Charts Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Unable to fetch charts data'}), 500

@app.route('/api/news', methods=['GET'])
@jwt_required()
def get_news():
    """Get finance news"""
    try:
        limit = request.args.get('limit', 5, type=int)
        return jsonify({'news': market_updates.get_finance_news(limit)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quote', methods=['GET'])
@jwt_required()
def get_quote():
    """Get motivational finance quote"""
    try:
        quote = nlp_processor.get_motivational_quote()
        return jsonify({'quote': quote}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Financial Mentor API is running'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

