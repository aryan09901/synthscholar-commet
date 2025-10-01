import time
import logging
from confection import Config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager # pyright: ignore[reportMissingImports]
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger(__name__)

class CometAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def initialize_browser(self):
        """Initialize Chrome browser for COMET interaction"""
        try:
            options = webdriver.ChromeOptions()
            
            if not Config.DEMO_MODE:
                options.add_argument('--headless')  # Run in background for production
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # Use webdriver_manager to automatically handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            
            logger.info("✅ Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize browser: {str(e)}")
            return False
    
    def login_to_comet(self, email, password):
        """Login to Perplexity COMET"""
        try:
            logger.info("🌐 Navigating to Perplexity...")
            self.driver.get("https://www.perplexity.ai")
            time.sleep(3)
            
            # Check if already logged in
            try:
                search_box = self.driver.find_element(By.XPATH, "//textarea[@placeholder='Ask anything...']")
                logger.info("✅ Already logged in to Perplexity")
                return True
            except:
                pass
            
            # Try to find and click login button
            login_selectors = [
                "//button[contains(., 'Login')]",
                "//button[contains(., 'Sign in')]",
                "//a[contains(., 'Login')]",
                "//a[contains(., 'Sign in')]"
            ]
            
            login_found = False
            for selector in login_selectors:
                try:
                    login_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    login_btn.click()
                    login_found = True
                    logger.info("✅ Login button clicked")
                    break
                except:
                    continue
            
            if not login_found:
                logger.warning("⚠️ Login button not found, might already be logged in")
                return True
            
            time.sleep(2)
            
            # Handle email input
            email_selectors = [
                "//input[@type='email']",
                "//input[@name='email']",
                "//input[@placeholder='Email']"
            ]
            
            for selector in email_selectors:
                try:
                    email_field = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    email_field.clear()
                    email_field.send_keys(email)
                    email_field.send_keys(Keys.RETURN)
                    logger.info("✅ Email entered")
                    break
                except:
                    continue
            
            time.sleep(3)
            
            logger.info("🔐 Please complete login manually if required...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Login failed: {str(e)}")
            return False
    
    def research_topic(self, topic):
        """Use COMET browser to research a topic comprehensively"""
        try:
            research_data = []
            
            # Navigate to Perplexity
            self.driver.get("https://www.perplexity.ai")
            time.sleep(3)
            
            # Sub-queries for comprehensive research
            sub_queries = [
                f"comprehensive analysis of {topic} with key benefits and advantages",
                f"main criticisms and challenges of {topic}",
                f"recent research and developments about {topic} in 2024",
                f"practical applications and real-world examples of {topic}",
                f"expert opinions and future outlook for {topic}"
            ]
            
            for i, query in enumerate(sub_queries):
                logger.info(f"🔍 Researching ({i+1}/{len(sub_queries)}): {query}")
                
                try:
                    # Find and clear search box
                    search_box = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//textarea[@placeholder='Ask anything...']"))
                    )
                    search_box.clear()
                    
                    # Type query character by character (more human-like)
                    for char in query:
                        search_box.send_keys(char)
                        time.sleep(0.05)
                    
                    search_box.send_keys(Keys.RETURN)
                    
                    # Wait for results - increased wait time
                    time.sleep(10)
                    
                    # Extract research content
                    content = self._extract_research_content()
                    if content and len(content) > 50:
                        research_data.append({
                            "sub_query": query,
                            "content": content
                        })
                        logger.info(f"✅ Retrieved content for: {query[:50]}...")
                    else:
                        logger.warning(f"⚠️ No substantial content for: {query}")
                    
                    # Wait between queries
                    time.sleep(3)
                    
                except Exception as query_error:
                    logger.error(f"❌ Query failed: {str(query_error)}")
                    continue
            
            logger.info(f"✅ Research completed. Gathered {len(research_data)} sections.")
            return research_data if research_data else None
            
        except Exception as e:
            logger.error(f"❌ Research failed: {str(e)}")
            return None
    
    def _extract_research_content(self):
        """Extract research content from COMET response"""
        try:
            # Multiple selectors for answer content
            selectors = [
                "//div[contains(@class, 'prose')]",
                "//div[contains(@class, 'answer')]",
                "//div[contains(@class, 'message')]",
                "//div[contains(@class, 'content')]",
                "//div[contains(@class, 'text')]",
                "//main//div[contains(@class, 'flex')]//div[contains(@class, 'flex')]"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        content = element.text.strip()
                        if content and len(content) > 200:  # Substantial content
                            return content
                except:
                    continue
            
            # Fallback: get all text from main content area
            try:
                main = self.driver.find_element(By.TAG_NAME, "main")
                content = main.text.strip()
                if content and len(content) > 100:
                    return content
            except:
                pass
            
            return "Research content extraction incomplete. Please try again."
            
        except Exception as e:
            logger.error(f"❌ Content extraction failed: {str(e)}")
            return "Unable to extract research content."
    
    def close_browser(self):
        """Close the browser session"""
        if self.driver:
            self.driver.quit()
            logger.info("🔚 Browser session closed")

class MockCometAutomation:
    """Mock version for reliable hackathon demo"""
    
    def __init__(self):
        self.mock_research_data = {
            "artificial intelligence": [
                {
                    "sub_query": "comprehensive analysis of artificial intelligence with key benefits and advantages",
                    "content": """Artificial Intelligence is transforming our world through machine learning, neural networks, and advanced algorithms. Key benefits include:

🚀 MAJOR ADVANTAGES:
• Automation of repetitive tasks across industries
• Enhanced decision-making through data analysis
• 24/7 operational capabilities without fatigue
• Personalization at scale for customer experiences
• Accelerated scientific research and drug discovery

💼 INDUSTRY IMPACT:
- Healthcare: AI diagnostics can detect diseases with 95%+ accuracy
- Finance: Fraud detection systems save billions annually
- Education: Personalized learning paths improve student outcomes by 40%
- Transportation: Self-driving vehicles could reduce accidents by 90%

📈 GROWTH METRICS:
AI market is projected to reach $1.5 trillion by 2030, with adoption growing at 35% annually across sectors."""
                },
                {
                    "sub_query": "main criticisms and challenges of artificial intelligence",
                    "content": """Despite its potential, AI faces significant challenges that require careful consideration:

⚠️ CRITICAL CONCERNS:
• Job displacement affecting 40% of current occupations
• Algorithmic bias perpetuating social inequalities
• Privacy erosion through mass data collection
• Black box problem - unexplainable decision-making
• Security vulnerabilities to adversarial attacks

🎯 ETHICAL DILEMMAS:
- Autonomous weapons and warfare applications
- Deepfakes undermining trust in media
- Surveillance capitalism and data exploitation
- Consent issues in data usage and model training

🛡️ MITIGATION STRATEGIES:
Strong regulatory frameworks, ethical AI guidelines, and transparent algorithms are essential for responsible AI development."""
                }
            ],
            "climate change": [
                {
                    "sub_query": "comprehensive analysis of climate change with key benefits and advantages of solutions",
                    "content": """Climate change represents humanity's greatest challenge, but solutions offer tremendous opportunities:

🌍 CURRENT STATUS:
• Global temperatures have risen 1.1°C since pre-industrial times
• Sea levels rising at 3.7mm annually, accelerating
• Extreme weather events increased 5x in 50 years
• Arctic sea ice declining 13% per decade

💡 SOLUTION BENEFITS:
Renewable energy adoption creates 3x more jobs than fossil fuels
Green technology market expected to reach $10 trillion by 2030
Air quality improvements could save 7 million lives annually
Energy independence through local renewable sources

🎯 KEY STRATEGIES:
• Solar and wind power now cheaper than fossil fuels
• Electric vehicle adoption growing 60% year-over-year
• Carbon capture technology advancing rapidly
• Sustainable agriculture practices increasing yields"""
                }
            ],
            "quantum computing": [
                {
                    "sub_query": "comprehensive analysis of quantum computing with key benefits and advantages",
                    "content": """Quantum computing leverages quantum mechanics to solve problems impossible for classical computers:

🔬 QUANTUM ADVANTAGE:
• Qubits can exist in superposition, enabling parallel computation
• Quantum entanglement allows instantaneous correlation
• Exponential speedup for specific problem classes
• Currently achieving 100+ qubit processors

💼 PRACTICAL APPLICATIONS:
- Drug discovery: Simulating molecular interactions
- Cryptography: Breaking current encryption, creating quantum-safe alternatives
- Optimization: Solving complex logistics and supply chain problems
- Financial modeling: Portfolio optimization and risk analysis

🏆 RECENT BREAKTHROUGHS:
Google's 70-qubit processor achieves 100 millionx speedup
IBM's 1000+ qubit processor planned for 2024
Quantum supremacy demonstrated for specific tasks"""
                }
            ]
        }
    
    def initialize_browser(self):
        print("✅ Mock COMET browser initialized")
        return True
    
    def login_to_comet(self, email, password):
        print(f"✅ Mock login successful for {email}")
        return True
    
    def research_topic(self, topic):
        topic_lower = topic.lower()
        
        # Find best matching topic
        for key in self.mock_research_data:
            if key in topic_lower:
                print(f"✅ Found mock research data for: {key}")
                return self.mock_research_data[key]
        
        # Generic response for unknown topics
        print(f"⚠️ Using generic mock data for: {topic}")
        return [
            {
                "sub_query": f"comprehensive analysis of {topic}",
                "content": f"""COMPREHENSIVE RESEARCH SUMMARY: {topic.upper()}

📊 EXECUTIVE OVERVIEW:
{topic} represents a significant technological/social/scientific advancement with far-reaching implications. Current adoption rates show 45% year-over-year growth across major industries.

🎯 KEY FINDINGS:
• Major efficiency improvements of 60-80% in target applications
• Cost reduction potential of 30-50% through automation
• Environmental impact reduction of 25% in sustainable implementations
• User satisfaction increases of 40% in deployed systems

🔬 TECHNICAL INSIGHTS:
Recent research from MIT, Stanford, and industry leaders demonstrates compelling evidence for widespread adoption. Peer-reviewed studies show consistent positive outcomes across multiple metrics.

💡 FUTURE OUTLOOK:
Market analysts project 10x growth in the next 5 years, with potential to disrupt traditional approaches and create new economic opportunities worth billions annually.

⚠️ CONSIDERATIONS:
Implementation requires careful planning, stakeholder buy-in, and addressing potential ethical concerns through transparent governance frameworks."""
            }
        ]
    
    def close_browser(self):
        print("🔚 Mock browser session closed")