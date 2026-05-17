"""
Translation Module
Handles multi-language support for the financial advisor bot
"""
import re

class Translator:
    def __init__(self):
        # Translation dictionaries for common financial terms and responses
        self.translations = {
            'hi': {  # Hindi
                'sip': 'एसआईपी',
                'mutual fund': 'म्यूचुअल फंड',
                'stocks': 'शेयर',
                'emi': 'ईएमआई',
                'interest': 'ब्याज',
                'investment': 'निवेश',
                'savings': 'बचत',
                'loan': 'कर्ज',
                'tax': 'कर',
                'retirement': 'सेवानिवृत्ति',
                'hello': 'नमस्ते',
                'how can i help': 'मैं आपकी कैसे मदद कर सकता हूं?',
                'greeting': 'नमस्ते! मैं आपका वित्तीय सलाहकार हूं।',
                'explain': 'व्याख्या करें',
                'calculate': 'गणना करें'
            },
            'te': {  # Telugu
                'sip': 'ఎస్‌ఐపి',
                'mutual fund': 'మ్యూచువల్ ఫండ్',
                'stocks': 'స్టాక్స్',
                'emi': 'ఇఎమ్ఐ',
                'interest': 'వడ్డీ',
                'investment': 'పెట్టుబడి',
                'savings': 'బచ్చత',
                'loan': 'రుణం',
                'tax': 'పన్ను',
                'retirement': 'విరమణ',
                'hello': 'నమస్కారం',
                'how can i help': 'నేను మీకు ఎలా సహాయం చేయగలను?',
                'greeting': 'నమస్కారం! నేను మీ ఆర్థిక సలహాదారుడిని.',
                'explain': 'వివరించండి',
                'calculate': 'లెక్కించండి'
            },
            'mr': {  # Marathi
                'sip': 'SIP',
                'mutual fund': 'म्यूच्युअल फंड',
                'stocks': 'शेअर्स',
                'emi': 'EMI',
                'interest': 'व्याज',
                'investment': 'गुंतवणूक',
                'savings': 'बचत',
                'loan': 'कर्ज',
                'tax': 'कर',
                'retirement': 'निवृत्ती',
                'hello': 'नमस्कार',
                'how can i help': 'मी तुम्हाला कसे मदत करू शकतो?',
                'greeting': 'नमस्कार! मी तुमचा आर्थिक सल्लागार आहे.',
                'explain': 'स्पष्ट करा',
                'calculate': 'मोजा'
            }
        }
        
        # Language-specific greeting responses
        self.greetings = {
            'en': [
                "Hello! I'm your Financial Mentor. How can I help you with your finances today?",
                "Hi there! I'm here to guide you through your financial journey. What would you like to know?",
            ],
            'hi': [
                "नमस्ते! मैं आपका वित्तीय सलाहकार हूं। आज मैं आपकी वित्तीय मदद कैसे कर सकता हूं?",
                "नमस्कार! मैं आपकी वित्तीय यात्रा में आपकी मदद के लिए यहां हूं। आप क्या जानना चाहेंगे?",
            ],
            'te': [
                "నమస్కారం! నేను మీ ఆర్థిక సలహాదారుడిని. నేను ఈరోజు మీకు ఆర్థికంగా ఎలా సహాయం చేయగలను?",
                "హలో! నేను మీ ఆర్థిక ప్రయాణంలో మీకు మార్గదర్శకత్వం చేయడానికి ఇక్కడ ఉన్నాను. మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?",
            ],
            'mr': [
                "नमस्कार! मी तुमचा आर्थिक सल्लागार आहे. आज मी तुम्हाला आर्थिकदृष्ट्या कसे मदत करू शकतो?",
                "हॅलो! मी तुमच्या आर्थिक प्रवासात तुम्हाला मार्गदर्शन करण्यासाठी इथे आहे. तुम्हाला काय जाणून घ्यायचे आहे?",
            ]
        }
        
        # Comprehensive translations for financial term explanations
        self.financial_explanations = {
            'hi': {
                'sip': """**एसआईपी (Systematic Investment Plan)** एक स्मार्ट निवेश रणनीति है जो आपको नियमित रूप से (आमतौर पर मासिक) म्यूचुअल फंड में एक निश्चित राशि निवेश करने की अनुमति देती है।

**मुख्य विशेषताएं:**
• **नियमित निवेश**: आप मासिक, साप्ताहिक या त्रैमासिक रूप से एक निश्चित राशि निवेश करते हैं
• **अनुशासन**: अनुशासित निवेश की आदत बनाने में मदद करता है
• **रुपया लागत औसत**: आप कम कीमत पर अधिक यूनिट और अधिक कीमत पर कम यूनिट खरीदते हैं
• **लचीलापन**: आप प्रति माह ₹500 से शुरुआत कर सकते हैं
• **शुरू करना आसान**: बैंकों, म्यूचुअल फंड कंपनियों या ऑनलाइन प्लेटफॉर्म के through सेट अप किया जा सकता है

**उदाहरण**: यदि आप हर महीने एक SIP में ₹5,000 निवेश करते हैं, तो आप बाजार की स्थितियों के बावजूद व्यवस्थित रूप से निवेश कर रहे हैं, जो समय के साथ आपके निवेश की लागत को औसत बनाने में मदद करता है।

क्या आप चाहते हैं कि मैं गणना करूं कि SIP के साथ आप कितना जमा कर सकते हैं?""",
                'emi': """**ईएमआई (Equated Monthly Installment)** ऋण चुकाने के लिए हर महीने एक निर्दिष्ट तारीख को उधारकर्ता द्वारा ऋणदाता को भुगतान की जाने वाली एक निश्चित राशि है।

**ईएमआई कैसे काम करता है:**
• **निश्चित राशि**: आप हर महीने समान राशि का भुगतान करते हैं
• **मूलधन + ब्याज**: प्रत्येक EMI में मूलधन चुकौती और ब्याज दोनों शामिल होते हैं
• **ऋण परिशोधन**: शुरुआत में, EMI का अधिकांश हिस्सा ब्याज में जाता है; समय के साथ, अधिक मूलधन में जाता है

**ईएमआई को प्रभावित करने वाले कारक:**
• **ऋण राशि**: अधिक ऋण = अधिक EMI
• **ब्याज दर**: अधिक दर = अधिक EMI
• **अवधि**: लंबी अवधि = कम EMI (लेकिन अधिक कुल ब्याज)

**उदाहरण**: 8% ब्याज पर 20 वर्षों के लिए ₹50 लाख के होम लोन के लिए, आपकी EMI लगभग ₹41,822 प्रति माह होगी।

क्या आप चाहते हैं कि मैं एक विशिष्ट ऋण राशि के लिए EMI की गणना करूं?""",
            },
            'te': {
                'sip': """**ఎస్‌ఐపి (Systematic Investment Plan)** అనేది మీకు నియమితంగా (సాధారణంగా నెలవారీ) మ్యూచువల్ ఫండ్లలో స్థిర మొత్తాన్ని పెట్టుబడి పెట్టడానికి అనుమతించే ఒక స్మార్ట్ పెట్టుబడి వ్యూహం.

**ప్రధాన లక్షణాలు:**
• **నియమిత పెట్టుబడులు**: మీరు నెలవారీ, వారంవారీ లేదా త్రైమాసికంగా స్థిర మొత్తాన్ని పెట్టుబడి పెడతారు
• **శిక్షణ**: నియమబద్ధమైన పెట్టుబడి అలవాటును నిర్మించడంలో సహాయపడుతుంది
• **రూపాయి ఖర్చు సగటు**: మీరు ధరలు తక్కువగా ఉన్నప్పుడు ఎక్కువ యూనిట్లు మరియు ధరలు ఎక్కువగా ఉన్నప్పుడు తక్కువ యూనిట్లు కొనుగోలు చేస్తారు
• **వశ్యత**: మీరు నెలకు ₹500 తో ప్రారంభించవచ్చు
• **ప్రారంభించడం సులభం**: బ్యాంకులు, మ్యూచువల్ ఫండ్ సంస్థలు లేదా ఆన్‌లైన్ ప్లాట్‌ఫారమ్ల ద్వారా సెటప్ చేయవచ్చు

**ఉదాహరణ**: మీరు ప్రతి నెల ఎస్‌ఐపిలో ₹5,000 పెట్టుబడి పెడితే, మీరు మార్కెట్ పరిస్థితులతో సంబంధం లేకుండా క్రమపద్ధతిగా పెట్టుబడి పెడుతున్నారు, ఇది కాలక్రమేణా మీ పెట్టుబడుల ఖర్చును సగటు చేయడంలో సహాయపడుతుంది.

మీరు ఎస్‌ఐపితో ఎంత సేకరించగలరో నేను లెక్కించాలనుకుంటున్నారా?""",
                'emi': """**ఇఎమ్ఐ (Equated Monthly Installment)** అనేది రుణాన్ని తిరిగి చెల్లించడానికి ప్రతి నెల నిర్దిష్ట తేదీన రుణగ్రహీత రుణదాతకు చెల్లించే స్థిర చెల్లింపు మొత్తం.

**ఇఎమ్ఐ ఎలా పని చేస్తుంది:**
• **స్థిర మొత్తం**: మీరు ప్రతి నెల అదే మొత్తాన్ని చెల్లిస్తారు
• **ప్రధాన + వడ్డీ**: ప్రతి EMI ప్రధాన వాపసు మరియు వడ్డీ రెండింటినీ కలిగి ఉంటుంది
• **రుణ తగ్గింపు**: ప్రారంభంలో, EMI యొక్క ఎక్కువ భాగం వడ్డీకి వెళుతుంది; కాలక్రమేణా, ఎక్కువ ప్రధానానికి వెళుతుంది

**EMIని ప్రభావితం చేసే అంశాలు:**
• **రుణ మొత్తం**: ఎక్కువ రుణం = ఎక్కువ EMI
• **వడ్డీ రేటు**: ఎక్కువ రేటు = ఎక్కువ EMI
• **కాలవ్యవధి**: పొడవైన కాలవ్యవధి = తక్కువ EMI (కానీ ఎక్కువ మొత్తం వడ్డీ)

**ఉదాహరణ**: 20 సంవత్సరాలకు 8% వడ్డీతో ₹50 లక్షల హోమ్‌లోన్ కోసం, మీ EMI నెలకు సుమారు ₹41,822 అవుతుంది.

నిర్దిష్ట రుణ మొత్తం కోసం EMIని నేను లెక్కించాలనుకుంటున్నారా?""",
            },
            'mr': {
                'sip': """**SIP (Systematic Investment Plan)** म्हणजे एक स्मार्ट गुंतवणूक रणनीती जी तुम्हाला नियमितपणे (सामान्यत: मासिक) म्यूच्युअल फंडमध्ये निश्चित रक्कम गुंतवण्याची परवानगी देते.

**मुख्य वैशिष्ट्ये:**
• **नियमित गुंतवणूक**: तुम्ही मासिक, साप्ताहिक किंवा त्रैमासिक नियमित रक्कम गुंतवता
• **शिस्त**: नियमित गुंतवणूकीची सवय तयार करण्यास मदत करते
• **रुपया खर्च सरासरी**: तुम्ही कमी किमतीत जास्त युनिट आणि जास्त किमतीत कमी युनिट खरेदी करता
• **लवचिकता**: तुम्ही ₹500 प्रति महिन्याने सुरू करू शकता
• **सुरू करणे सोपे**: बँकांद्वारे, म्यूच्युअल फंड कंपन्या किंवा ऑनलाइन प्लॅटफॉर्मद्वारे सेट अप केले जाऊ शकते

**उदाहरण**: जर तुम्ही प्रत्येक महिन्याला SIP मध्ये ₹5,000 गुंतवता, तर तुम्ही बाजाराच्या परिस्थितीची पर्वा न करता नियमितपणे गुंतवणूक करत आहात, जे कालांतराने तुमच्या गुंतवणुकीचा खर्च सरासरी करण्यास मदत करते.

तुम्हाला SIP सह किती जमा करता येईल याची गणना करायची आहे का?""",
                'emi': """**EMI (Equated Monthly Installment)** म्हणजे महिन्याच्या एका निर्दिष्ट तारखेला रुण फेडण्यासाठी उधार घेणाऱ्याद्वारे देणाऱ्याला केलेली निश्चित देय रक्कम.

**EMI कसे काम करते:**
• **निश्चित रक्कम**: तुम्ही प्रत्येक महिन्याला समान रक्कम भरता
• **प्रधान + व्याज**: प्रत्येक EMI मध्ये प्रधान परतफेड आणि व्याज दोन्ही समाविष्ट असतात
• **परिशोधन**: सुरुवातीला, EMI चा बहुतेक भाग व्याजाकडे जातो; कालांतराने, अधिक प्रधानाकडे जाते

**EMI ला प्रभावित करणारे घटक:**
• **कर्ज रक्कम**: जास्त कर्ज = जास्त EMI
• **व्याज दर**: जास्त दर = जास्त EMI
• **कालावधी**: लांब कालावधी = कमी EMI (परंतु जास्त एकूण व्याज)

**उदाहरण**: 20 वर्षांसाठी 8% व्याजावर ₹50 लाख घर कर्जासाठी, तुमची EMI दरमहा सुमारे ₹41,822 असेल.

तुम्हाला विशिष्ट कर्ज रकमेसाठी EMI ची गणना करायची आहे का?""",
            }
        }
    
    def detect_language(self, text):
        """Detect the language of the input text"""
        # Simple detection based on character ranges
        text = text.strip()
        
        # Hindi detection (Devanagari script: 0900-097F)
        if re.search(r'[\u0900-\u097F]', text):
            return 'hi'
        
        # Telugu detection (Telugu script: 0C00-0C7F)
        if re.search(r'[\u0C00-\u0C7F]', text):
            return 'te'
        
        # Tamil (optional)
        if re.search(r'[\u0B80-\u0BFF]', text):
            return 'ta'
        
        # Default to English
        return 'en'
    
    def translate_term(self, term, target_lang='en'):
        """Translate a financial term to target language"""
        if target_lang == 'en':
            return term
        
        term_lower = term.lower().strip()
        if target_lang in self.translations and term_lower in self.translations[target_lang]:
            return self.translations[target_lang][term_lower]
        
        return term  # Return original if translation not found
    
    def get_greeting(self, lang='en'):
        """Get greeting in specified language"""
        import random
        if lang in self.greetings:
            return random.choice(self.greetings[lang])
        return random.choice(self.greetings['en'])
    
    def get_financial_explanation(self, term, target_lang='en'):
        """Get translated financial term explanation"""
        if target_lang == 'en':
            return None  # Will use original English explanation
        
        term_lower = term.lower().strip()
        if target_lang in self.financial_explanations:
            if term_lower in self.financial_explanations[target_lang]:
                return self.financial_explanations[target_lang][term_lower]
        
        return None
    
    def translate_response(self, response_text, target_lang='en', term=None):
        """Translate response text to target language"""
        if target_lang == 'en':
            return response_text
        
        # First check if we have a pre-translated explanation for this financial term
        if term:
            translated_explanation = self.get_financial_explanation(term, target_lang)
            if translated_explanation:
                return translated_explanation
        
        # For other responses, use basic translation patterns
        # Common phrases translation
        translations_map = {
            'hi': {
                'calculation results:': 'गणना परिणाम:',
                'emi:': 'ईएमआई:',
                'total payment:': 'कुल भुगतान:',
                'total interest:': 'कुल ब्याज:',
                'total invested:': 'कुल निवेश:',
                'maturity amount:': 'परिपक्वता राशि:',
                'gains:': 'लाभ:',
                'return:': 'रिटर्न:',
                'would you like': 'क्या आप चाहेंगे',
                'i\'d be happy to explain': 'मुझे समझाने में खुशी होगी',
            },
            'te': {
                'calculation results:': 'లెక్కల ఫలితాలు:',
                'emi:': 'ఇఎమ్ఐ:',
                'total payment:': 'మొత్తం చెల్లింపు:',
                'total interest:': 'మొత్తం వడ్డీ:',
                'total invested:': 'మొత్తం పెట్టుబడి:',
                'maturity amount:': 'మెచ్యోరిటీ మొత్తం:',
                'gains:': 'లాభాలు:',
                'return:': 'రాబడి:',
                'would you like': 'మీకు కావలసిన',
                'i\'d be happy to explain': 'వివరించడంలో నాకు సంతోషం',
            },
            'mr': {
                'calculation results:': 'गणना परिणाम:',
                'emi:': 'EMI:',
                'total payment:': 'एकूण देय:',
                'total interest:': 'एकूण व्याज:',
                'total invested:': 'एकूण गुंतवणूक:',
                'maturity amount:': 'परिपक्वता रक्कम:',
                'gains:': 'नफा:',
                'return:': 'परतावा:',
                'would you like': 'तुम्हाला हवे आहे',
                'i\'d be happy to explain': 'स्पष्ट करण्यात आनंद होईल',
            }
        }
        
        # Simple translation for common phrases (basic approach)
        # For production, integrate Google Translate API or similar
        result = response_text
        if target_lang in translations_map:
            for eng_phrase, translated in translations_map[target_lang].items():
                # Case-insensitive replacement
                import re
                pattern = re.compile(re.escape(eng_phrase), re.IGNORECASE)
                result = pattern.sub(translated, result)
        
        # If no translation found and no term match, return English
        # In production, you'd use a translation API here
        return result if result != response_text else response_text
