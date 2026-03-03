# The ultimate dataset list for AI sales and marketing fine-tuning

**This collection spans 100+ unique, openly available datasets across sales psychology, advertising, copywriting, persuasion, consumer behavior, and marketing NLP.** Each dataset listed below includes a direct link and brief description to help you evaluate fit for fine-tuning. Sources span Hugging Face, Kaggle, GitHub, UCI Machine Learning Repository, Cornell, Stanford, and academic archives. The datasets range from small curated corpora of ~700 examples to massive collections with billions of data points.

---

## Sales conversations and dialogue datasets

These datasets capture real and synthetic sales interactions—conversations, transcripts, and CRM records—ideal for training an AI to handle objections, build rapport, and close deals.

**1. Sales Conversations (goendalf666)**
3,410 synthetic sales conversations between customer and salesman, generated using GPT-3.5-turbo for training a persuasive sales chatbot. Based on the "Textbooks Is All You Need" methodology.
**URL:** https://huggingface.co/datasets/goendalf666/sales-conversations

**2. Sales Conversations Instruction-Customer (goendalf666)**
**20,900 instruction-formatted** sales conversation examples derived from dataset #1, structured for instruction-tuning an LLM to respond as a persuasive salesman to customer statements.
**URL:** https://huggingface.co/datasets/goendalf666/sales-conversations-instruction-customer

**3. Sales Textbook for Convincing and Selling (goendalf666)**
Synthetic textbook covering rapport building, communication skills, discovering needs, presenting solutions, overcoming objections, and closing the sale. Foundation knowledge for sales AI training.
**URL:** https://huggingface.co/datasets/goendalf666/sales-textbook_for_convincing_and_selling

**4. SaaS Sales Conversations (DeepMostInnovations)**
Large-scale synthetic dataset of **SaaS sales dialogues** generated with GPT-4. Includes conversation outcomes and engagement metrics, designed for sales conversion prediction and reinforcement learning.
**URL:** https://huggingface.co/datasets/DeepMostInnovations/saas-sales-conversations

**5. Sales Transcripts (gwenshap)**
Simulated sales conversations for 5 fictional companies, including chunked and embedded versions using OpenAI's text-embedding-3-small model. Ready for vector database loading.
**URL:** https://huggingface.co/datasets/gwenshap/sales-transcripts

**6. CallCenterEN — 92K Real-World Call Center Transcripts (AIxBlock)**
**91,706 real-world English call center transcripts** (~10,448 audio hours) across 9 commercial domains including sales, insurance, and automotive. PII-redacted with word-level timestamps. CC BY-NC 4.0 license.
**URL:** https://huggingface.co/datasets/AIxBlock/92k-real-world-call-center-scripts-english

**7. English Contact Center Audio Dataset (AxonData)**
1,000+ hours of real-world call center audio with transcripts covering sales (product inquiries, upselling, cross-selling), billing, and finance. Includes agent/customer role annotations.
**URL:** https://huggingface.co/datasets/AxonData/english-contact-center-audio-dataset

**8. Bitext Customer Support LLM Chatbot Training Dataset**
**27,000+ customer service Q&A pairs** covering 27 intents across 10 categories (cancel_order, place_order, track_order, get_refund, etc.) with linguistic variation tags. Designed for fine-tuning customer-facing chatbots across 20 industry verticals.
**URL:** https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset

**9. PolyAI Conversational Datasets (GitHub)**
Tools and scripts to create large-scale conversational datasets including Reddit (3.7B comments), OpenSubtitles (400M+ lines), and **Amazon QA (3.6M+ product question-response pairs)**—the latter being particularly relevant for sales Q&A training.
**URL:** https://github.com/PolyAI-LDN/conversational-datasets

---

## Negotiation and persuasion technique datasets

These datasets are the core of persuasion science—annotated dialogues, argument structures, and persuasive strategy corpora essential for teaching an AI the mechanics of influence.

**10. CraigslistBargains (Stanford NLP)**
**6,682 human-human negotiation dialogues** where buyer and seller negotiate item prices from Craigslist across 6 categories. Features persuasion techniques like embellishment, with dialogue act annotations.
**URL:** https://huggingface.co/datasets/stanfordnlp/craigslist_bargains

**11. CaSiNo — Campsite Negotiation Dialogues**
1,030 negotiation dialogues with rich metadata including Big-5 personality traits, Social Value Orientation, and **per-utterance persuasion strategy annotations**. Published at NAACL 2021.
**URL:** https://huggingface.co/datasets/kchawla123/casino

**12. Deal or No Deal — Negotiation Dialogues (Facebook AI Research)**
**5,808 human-human negotiation dialogues** on a multi-issue bargaining task where agents with hidden reward functions must reach agreements via natural language.
**URL:** https://huggingface.co/datasets/mikelewis0/deal_or_no_dialog

**13. Facebook End-to-End Negotiator (GitHub)**
Original codebase and dataset (5,808 dialogues, 2,236 scenarios) from FAIR's "Deal or No Deal?" paper. Includes training code for negotiation agents, RL self-play, and dialogue rollout planning.
**URL:** https://github.com/facebookresearch/end-to-end-negotiator

**14. Persuasion for Good**
**1,017 persuasion dialogues** where one participant convinces the other to donate to charity. Annotated with 10 persuasion strategies, participant demographics, Big-5 traits, and donation outcomes. Landmark ACL 2019 dataset.
**URL:** https://huggingface.co/datasets/spawn99/PersuasionForGood

**15. Anthropic Persuasion Dataset**
~3,940 examples covering 75 claims with human-written and LLM-generated persuasive arguments, plus **persuasiveness scores** (initial and final stance ratings). Directly applicable to marketing copy optimization.
**URL:** https://huggingface.co/datasets/Anthropic/persuasion

**16. SemEval-2020 Task 11 — Propaganda Technique Detection**
News articles annotated for **18 propaganda/persuasion techniques** (Appeal to Authority, Loaded Language, Bandwagon, Flag-Waving, etc.) with span-level annotations. Over 250 participating teams.
**URL:** https://huggingface.co/datasets/SemEvalWorkshop/sem_eval_2020_task_11

**17. Winning Arguments — ChangeMyView Corpus (Cornell)**
**293,297 utterances** across 3,051 conversations from Reddit's r/ChangeMyView, tracking whether counter-arguments successfully changed the OP's view. Paired successful/unsuccessful argument threads for studying persuasion dynamics.
**URL:** https://convokit.cornell.edu/documentation/winning.html

**18. PersuasionBench & PersuasionArena**
Benchmark for evaluating and enhancing persuasion in text, including "transsuasion" (transforming non-persuasive text into persuasive text). From the 2024 paper "Measuring and Improving Persuasiveness of Large Language Models."
**URL:** https://behavior-in-the-wild.github.io/measure-persuasion

**19. DebateSum (GitHub)**
**187,386 unique pieces of debate evidence** with argument and extractive summaries, compiled from National Speech and Debate Association competitors over 7 years. Trains models to understand argument structure.
**URL:** https://github.com/Hellisotherpeople/DebateSum

**20. OpenDebateEvidence**
Massive-scale argument mining dataset with **3.5+ million documents** from American competitive debate. One of the most extensive collections of structured argumentative evidence.
**URL:** https://arxiv.org/abs/2406.14657

---

## CRM, sales pipeline, and business email data

Structured datasets for understanding deal flow, pipeline metrics, and business communication patterns.

**21. Sales Pipeline Dataset (Kaggle)**
Sales pipeline data for analyzing deal stages, conversion rates, and pipeline performance metrics.
**URL:** https://www.kaggle.com/datasets/ashishpandey5210/sales-pipeline-dataset

**22. CRM Sales Opportunities (Kaggle)**
CRM dataset with sales opportunities data for analyzing sales performance, opportunity management, and predictive analytics.
**URL:** https://www.kaggle.com/datasets/innocentmfa/crm-sales-opportunities

**23. B2B Sales Pipeline Data (Maven Analytics)**
B2B sales pipeline from a fictitious computer hardware company. Practice-ready dataset for analyzing deal flow and win/loss rates.
**URL:** https://mavenanalytics.io/data-playground

**24. Enron Email Dataset (Kaggle)**
**~500,000 emails** from 150 Enron employees—one of the largest publicly available email datasets. Contains real corporate communications including sales discussions and negotiations.
**URL:** https://www.kaggle.com/datasets/wcukierski/enron-email-dataset

**25. Annotated Enron Subject Line Corpus — AESLC (Yale-LILY)**
Email bodies paired with subject lines from Enron, designed for email subject line generation tasks. ACL 2019 benchmark.
**URL:** https://huggingface.co/datasets/Yale-LILY/aeslc

---

## Facebook/Meta Ads campaign datasets

**26. Facebook Ad Campaign (Kaggle)**
Ad campaign data with impressions, clicks, spend, conversions (total and approved), segmented by **age, gender, and interest categories**. Ideal for conversion rate analysis.
**URL:** https://www.kaggle.com/datasets/madislemsalu/facebook-ad-campaign

**27. Facebook Ads Dataset (Kaggle — Aparna Shankar)**
Facebook advertising dataset for analysis of ad performance metrics and audience targeting.
**URL:** https://www.kaggle.com/datasets/aparnashankar/facebook-ads-dataset

**28. Political Advertisements from Facebook (Kaggle)**
Political advertisements run on Facebook—useful for studying ad content, targeting strategies, and political marketing.
**URL:** https://www.kaggle.com/datasets/mrmorj/political-advertisements-from-facebook

---

## Google Ads performance datasets

**29. Google Ads (Kaggle — Dan Kawaguchi)**
Google Ads campaign performance data including cost, clicks, and conversion metrics.
**URL:** https://www.kaggle.com/datasets/dankawaguchi/google-ads

**30. Google Ads Sales Dataset (Kaggle)**
Links Google Ads campaign data to sales outcomes for ROI analysis.
**URL:** https://www.kaggle.com/datasets/nayakganesh007/google-ads-sales-dataset

**31. Google Ad Costs (Kaggle)**
Cost-per-click and keyword pricing data exploring the cost of advertising on Google.
**URL:** https://www.kaggle.com/datasets/brendan45774/how-much-it-cost-to-get-an-ad-on-google

---

## Ad copy, creative text, and programmatic advertising datasets

These are the datasets most directly useful for training an AI to write ad copy—real-world creative text from programmatic ads and instruction-tuned ad generation examples.

**32. Ad Copy Generation (smangrul)**
**~1,140 instruction-tuned ad copy examples** formatted for Llama V2 chat template. Each sample contains product name, description, and creative ad text.
**URL:** https://huggingface.co/datasets/smangrul/ad-copy-generation

**33. Ads Creative Ad Copy Programmatic (PeterBrendan)**
7,097 samples of real-world programmatic ad copy with ad sizes (300x250, 728x90, etc.). MIT licensed.
**URL:** https://huggingface.co/datasets/PeterBrendan/Ads_Creative_Ad_Copy_Programmatic

**34. Ads Creative Text Programmatic (PeterBrendan)**
Programmatic ad creative text for language modeling, text generation, and augmentation tasks. MIT licensed.
**URL:** https://huggingface.co/datasets/PeterBrendan/Ads_Creative_Text_Programmatic

**35. AdImageNet (PeterBrendan)**
**9,003 samples** of online programmatic ad creatives with ad sizes, extracted text, and images. Modeled after ImageNet's approach for advertising research.
**URL:** https://huggingface.co/datasets/PeterBrendan/AdImageNet

**36. AdTEC — Ad Text Evaluation Corpus (CyberAgent)**
Benchmark for evaluating ad text quality in search engine advertising, with ad acceptability classification tasks.
**URL:** https://huggingface.co/datasets/cyberagent/AdTEC

**37. Product Descriptions and Ads (c-s-ale)**
100 clothing product descriptions paired with generated advertisements—useful for training product-to-ad generation.
**URL:** https://huggingface.co/datasets/c-s-ale/Product-Descriptions-and-Ads

**38. Bad News: Clickbait and Deceptive Ads Dataset (GitHub)**
Research dataset on clickbait and deceptive advertising with labeled screenshots, landing pages, ad platform metadata, and ad type classifications.
**URL:** https://github.com/eric-zeng/conpro-bad-ads-data

---

## Marketing campaign and digital marketing conversion datasets

**39. Marketing Campaign Performance Dataset (Kaggle)**
Performance metrics across multiple channels and campaign types.
**URL:** https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset

**40. Marketing Campaign Dataset (Kaggle — Rahul Chavan)**
Customer-level data including demographics, purchase history, income, spending patterns, and **campaign acceptance rates**.
**URL:** https://www.kaggle.com/datasets/rahulchavan99/marketing-campaign-dataset

**41. Predict Conversion in Digital Marketing (Kaggle)**
**8,000 records** with 20 columns covering customer interactions, demographics, marketing metrics, engagement indicators, and binary conversion target.
**URL:** https://www.kaggle.com/datasets/rabieelkharoua/predict-conversion-in-digital-marketing-dataset

**42. Digital Marketing Dataset (Kaggle — Ally Jung)**
Digital marketing performance and conversion optimization data.
**URL:** https://www.kaggle.com/datasets/allyjung81/digital-marketing-dataset

**43. Social Media Ad Dataset (Kaggle)**
User engagement, ad performance, and conversion tracking from social media campaigns.
**URL:** https://www.kaggle.com/datasets/ziya07/social-media-ad-dataset

**44. Advertising Dataset — TV, Radio, Newspaper (Kaggle)**
Classic dataset from the ISLR textbook linking TV, radio, and newspaper ad spend to sales. Standard benchmark for **marketing mix modeling**.
**URL:** https://www.kaggle.com/datasets/ashydv/advertising-dataset

---

## Social media and email marketing datasets

**45. Marketing Social Media (RafaM97)**
689 marketing content generation examples with industry, channel (Facebook, Twitter, Instagram), campaign objective (brand awareness, lead generation, retention), and generated marketing copy.
**URL:** https://huggingface.co/datasets/RafaM97/marketing_social_media

**46. Email Campaign Management for SME (Kaggle)**
Email campaign data including open rates, click rates, and customer engagement metrics for predicting campaign effectiveness.
**URL:** https://www.kaggle.com/datasets/loveall/email-campaign-management-for-sme

**47. Email Marketing Campaign Dashboard (Kaggle)**
Dashboard-ready data with delivery, open, click, and conversion metrics.
**URL:** https://www.kaggle.com/datasets/mariusnikiforovas/email-marketing-campaign-dashboard

---

## A/B testing datasets

**48. Marketing A/B Testing (Kaggle)**
Classic A/B test comparing ads vs. public service announcements. Contains user IDs, test groups, conversion status, and total ads seen—ideal for learning **experimental design in marketing**.
**URL:** https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing

**49. A/B Testing Dataset (Kaggle — Amir Motefaker)**
General A/B testing dataset for evaluating marketing interventions and landing page performance.
**URL:** https://www.kaggle.com/datasets/amirmotefaker/ab-testing-dataset

---

## Click-through rate prediction and online advertising data

These massive-scale datasets are industry-standard benchmarks for understanding what drives clicks—critical for ad optimization AI.

**50. Criteo Click Logs (Hugging Face)**
Massive display ad click logs covering **24 days of Criteo traffic**. Each row has click/no-click label, 13 integer features, and 26 categorical features. Industry-standard CTR benchmark.
**URL:** https://huggingface.co/datasets/criteo/CriteoClickLogs

**51. Criteo Display Advertising Challenge (Kaggle)**
**~45 million samples** for CTR prediction with anonymized numerical and categorical features. One of the most widely used ad prediction benchmarks.
**URL:** https://www.kaggle.com/c/criteo-display-ad-challenge/data

**52. CriteoPrivateAd (Hugging Face)**
Largest real-world anonymized bidding dataset for designing **private advertising systems**, aligned with Chrome Privacy Sandbox and browser privacy proposals.
**URL:** https://huggingface.co/datasets/criteo/CriteoPrivateAd

**53. Advertisement Click on Ad (Kaggle)**
Clean binary classification dataset predicting ad clicks based on user features (age, income, daily internet usage).
**URL:** https://www.kaggle.com/datasets/gabrielsantello/advertisement-click-on-ad

**54. Click-Through Rate Prediction (Kaggle — Swekerr)**
CTR prediction dataset with user behavior and ad interaction features.
**URL:** https://www.kaggle.com/datasets/swekerr/click-through-rate-prediction

**55. Avazu CTR Prediction Dataset (Kaggle)**
Large-scale mobile advertising CTR dataset with **10 days of click data** including ad, device, and user interaction features.
**URL:** https://www.kaggle.com/c/avazu-ctr-prediction/

**56. TalkingData AdTracking Fraud Detection (Kaggle)**
**200M+ rows** of mobile ad click fraud detection data with IP, app, device, OS, channel, and timestamps.
**URL:** https://www.kaggle.com/c/talkingdata-adtracking-fraud-detection/data

**57. Ads & RecSys Datasets Collection (GitHub)**
Repository collecting multiple ad and recommendation datasets (iPinYou, Criteo, Avazu, Criteo Challenge) in standardized HDF5 format.
**URL:** https://github.com/Atomu2014/Ads-RecSys-Datasets

---

## Copywriting datasets: headlines, slogans, and product descriptions

**58. Clickbait Dataset (Kaggle)**
**~32,000 headlines** classified as clickbait vs. non-clickbait—useful for understanding attention-grabbing writing patterns.
**URL:** https://www.kaggle.com/datasets/amananandrai/clickbait-dataset

**59. Clickbait Corpus (GitHub — bhargaviparanjape)**
32,000 article headlines (16,000 clickbait from BuzzFeed/Upworthy, 16,000 non-clickbait from WikiNews/NY Times). Published at ASONAM 2016.
**URL:** https://github.com/bhargaviparanjape/clickbait

**60. News Headlines for Sarcasm Detection (Kaggle)**
Headlines from TheOnion (sarcastic) and HuffPost (non-sarcastic)—useful for understanding tone and creative headline writing.
**URL:** https://www.kaggle.com/datasets/rmisra/news-headlines-dataset-for-sarcasm-detection

**61. English Headlines Dataset (Kaggle)**
Collection of English news headlines for text analysis and headline generation tasks.
**URL:** https://www.kaggle.com/datasets/anil1055/english-headlines-dataset

**62. Slogan Dataset (Kaggle)**
Advertising slogans and brand taglines for training slogan generation or studying effective marketing language.
**URL:** https://www.kaggle.com/datasets/chaibapat/slogan-dataset

**63. Amazon Product Descriptions (Ateeqq)**
**421K unique cleaned Amazon product descriptions** (from 10M+ dataset). Descriptions under 200 characters removed. CC-BY-NC-SA-4.0 license.
**URL:** https://huggingface.co/datasets/Ateeqq/Amazon-Product-Description

**64. Amazon Product Descriptions VLM (philschmid)**
Slim version of Amazon product descriptions optimized for multimodal LLM training, pairing product images with marketing-ready descriptions.
**URL:** https://huggingface.co/datasets/philschmid/amazon-product-descriptions-vlm

**65. Amazon Product Data (Kaggle — 10M+)**
Large-scale Amazon product dataset with titles, descriptions, and metadata.
**URL:** https://www.kaggle.com/datasets/piyushjain16/amazon-product-data

**66. Copywriting Dataset (suolyer)**
Copywriting-focused dataset for text generation tasks related to marketing and advertising.
**URL:** https://huggingface.co/datasets/suolyer/copywriting

**67. Social Media Post Generator Dataset (Kaggle)**
Raw and enriched social media posts for AI-driven content creation and marketing copy generation.
**URL:** https://www.kaggle.com/datasets/prishatank/post-generator-dataset

---

## Consumer behavior and purchase decision datasets

**68. Consumer Behavior and Shopping Habits (Kaggle)**
Purchase amounts, review ratings, subscription status, payment methods, shipping, discount usage, purchase frequency, and demographics.
**URL:** https://www.kaggle.com/datasets/zeesolver/consumer-behavior-and-shopping-habits-dataset

**69. E-Commerce Customer Behavior (Kaggle)**
Customer demographics plus behavioral data: total spend, items purchased, average rating, membership type.
**URL:** https://www.kaggle.com/datasets/uom190346a/e-commerce-customer-behavior-dataset

**70. Online Shoppers Purchasing Intention (UCI)**
**12,330 sessions** with page visits, durations, bounce rates, exit rates, and binary purchase label. Standard benchmark for purchase prediction.
**URL:** https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset

**71. Predict Customer Purchase Behavior (Kaggle)**
Demographic and behavioral attributes for building purchase prediction models.
**URL:** https://www.kaggle.com/datasets/rabieelkharoua/predict-customer-purchase-behavior-dataset

**72. Customer Purchasing Behaviors (Kaggle)**
Purchase frequency, amounts, product preferences, and demographics for modeling consumer decision-making.
**URL:** https://www.kaggle.com/datasets/hanaksoy/customer-purchasing-behaviors

**73. AI-Driven Consumer Behavior Dataset (Kaggle)**
Clickstream data, reviews, demographics, and browsing habits for AI-driven consumer analysis.
**URL:** https://www.kaggle.com/datasets/ziya07/ai-driven-consumer-behavior-dataset

**74. Online Shopping Consumer Behavior (Kaggle)**
Browsing behavior, purchase patterns, and consumer preferences in digital retail.
**URL:** https://www.kaggle.com/datasets/thedevastator/online-shopping-consumer-behavior-dataset

---

## E-commerce behavior and customer journey datasets

**75. eCommerce Behavior Data — Multi-Category Store (REES46/Kaggle)**
**~285 million user events** (product views, cart additions, purchases) with timestamps, product IDs, categories, brands, and prices. Ideal for funnel analysis and customer journey modeling.
**URL:** https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store

**76. Online Retail Dataset (UCI)**
**541,909 transactions** from a UK online retailer (Dec 2010–Dec 2011). Widely used for customer segmentation (RFM analysis) and market basket analysis.
**URL:** https://archive.ics.uci.edu/dataset/352/online+retail

**77. Instacart Market Basket Analysis (Kaggle)**
**3+ million grocery orders** from 200K+ users across 50K unique products. Contains order sequences, timing, and reorder patterns.
**URL:** https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis

**78. Clickstream Data for Online Shopping (Kaggle)**
Detailed user navigation data including page views, sessions, and purchase outcomes.
**URL:** https://www.kaggle.com/datasets/tunguz/clickstream-data-for-online-shopping

**79. Retailrocket Recommender System Dataset (Kaggle)**
Real-world e-commerce data (views, add-to-cart, transactions) collected over 4.5 months with item properties and category hierarchy.
**URL:** https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset

---

## Customer churn and segmentation datasets

**80. Telco Customer Churn (Kaggle)**
**7,043 rows** with demographics, account info, and service usage. Binary churn target. One of the most popular churn prediction benchmarks.
**URL:** https://www.kaggle.com/datasets/blastchar/telco-customer-churn

**81. Iranian Churn Dataset (UCI)**
3,150 telecom customer records with 13 features including complaints, usage, and subscription data.
**URL:** https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset

**82. Mall Customer Segmentation (Kaggle)**
200 mall customers with age, income, and spending score—classic clustering/segmentation dataset.
**URL:** https://www.kaggle.com/datasets/vjchoudhary7/customer-segmentation-tutorial-in-python

**83. Customer Segmentation Classification (Kaggle)**
Demographics, spending behavior, and membership features for segment classification models.
**URL:** https://www.kaggle.com/datasets/kaushiksuresh147/customer-segmentation

---

## Product review and sentiment analysis datasets

These large-scale review corpora are essential for training an AI to understand customer language, satisfaction drivers, and sentiment—core knowledge for persuasive marketing.

**84. Amazon Reviews 2023 (McAuley Lab)**
The largest Amazon review dataset: **10B+ data points** spanning May 1996–September 2023. Includes ratings, review text, helpfulness votes, product metadata, prices, and images across 33 categories.
**URL:** https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023

**85. Amazon Polarity**
**4 million Amazon reviews** with binary positive/negative labels. Apache-2.0 license.
**URL:** https://huggingface.co/datasets/fancyzhx/amazon_polarity

**86. Amazon Reviews for Sentiment Analysis (Kaggle)**
Amazon reviews formatted for sentiment analysis with labeled polarity.
**URL:** https://www.kaggle.com/datasets/bittlingmayer/amazonreviews

**87. Stanford Amazon Product Data (SNAP)**
**143.7 million Amazon reviews** (1996–2014) with ratings, text, metadata, and product relationship graphs. A foundational dataset for product NLP.
**URL:** https://snap.stanford.edu/data/amazon/productGraph/

**88. Yelp Review Full**
**700,000 Yelp reviews** with 5-star ratings from the Yelp Dataset Challenge 2015. Excellent for understanding customer satisfaction in service businesses.
**URL:** https://huggingface.co/datasets/Yelp/yelp_review_full

**89. Yelp Polarity**
Binary sentiment version of Yelp reviews (560K training, 38K testing).
**URL:** https://huggingface.co/datasets/fancyzhx/yelp_polarity

**90. Women's E-Commerce Clothing Reviews (Kaggle)**
**23,486 real customer reviews** from a women's clothing retailer with ratings, recommendations, and product category data.
**URL:** https://www.kaggle.com/datasets/nicapotato/womens-ecommerce-clothing-reviews

**91. Stanford Sentiment Treebank (SST-2)**
Classic benchmark with ~11,855 movie review sentences and fine-grained sentiment annotations. Foundational for sentiment model evaluation.
**URL:** https://huggingface.co/datasets/stanfordnlp/sst2

**92. IMDB Movie Reviews**
**50,000 polar movie reviews** (25K train, 25K test). Foundational binary sentiment benchmark adaptable to product/service review analysis.
**URL:** https://huggingface.co/datasets/mteb/imdb

**93. Financial Sentiment Analysis**
Financial news headlines with positive/negative/neutral sentiment from a retail investor perspective. Useful for financial services marketing.
**URL:** https://huggingface.co/datasets/mltrev23/financial-sentiment-analysis

**94. Multiclass Sentiment Analysis Dataset**
**105K examples** across 3 sentiment categories with balanced splits.
**URL:** https://huggingface.co/datasets/Sp1786/multiclass-sentiment-analysis-dataset

---

## Social media NLP and brand monitoring datasets

**95. Sentiment140 (Twitter/Stanford)**
**1.6 million tweets** annotated for sentiment using distant supervision. Industry standard for social media sentiment models.
**URL:** https://huggingface.co/datasets/stanfordnlp/sentiment140

**96. TweetEval Benchmark (Cardiff NLP)**
Unified benchmark of **7 tweet classification tasks**: sentiment, emotion, irony, hate speech, offensive language, emoji prediction, and stance detection. Essential for social media marketing NLP.
**URL:** https://huggingface.co/datasets/cardiffnlp/tweet_eval

**97. Twitter Sentiment Analysis Corpus**
**1.58 million classified tweets** with binary positive/negative labels.
**URL:** https://huggingface.co/datasets/carblacac/twitter-sentiment-analysis

**98. BRAND Database — Brand Recognition and Attitude Norms**
Consumer responses to **500+ top brands and logos** across 32 industries, measuring familiarity, liking, and memory from 2,000 US consumers.
**URL:** https://pubmed.ncbi.nlm.nih.gov/39681772/

---

## Aspect-based sentiment and opinion mining datasets

**99. SemEval-2014 ABSA — Restaurants & Laptops (SetFit format)**
Aspect-based sentiment analysis with aspect terms, categories, and per-aspect sentiment polarities for restaurant and laptop reviews. Ready for few-shot ABSA training.
**URL:** https://huggingface.co/docs/setfit/en/how_to/absa

**100. Chat-Based Aspect Sentiment Analysis**
**28,800 rows** covering multiple ABSA sub-tasks: Aspect Term Extraction, Opinion Term Extraction, Triplet Extraction, and Quadruple Extraction. MIT license.
**URL:** https://huggingface.co/datasets/yuncongli/chat-sentiment-analysis

---

## Stance detection and argument mining for persuasion

**101. SemEval-2016 Task 6 — Stance Detection in Tweets**
Foundational benchmark for stance detection (Favor, Against, Neither) toward 5 targets. Applicable to brand perception monitoring and campaign analysis.
**URL:** https://saifmohammad.com/WebPages/StanceDataset.htm

**102. X-Stance — Multilingual Stance Detection (ZurichNLP)**
**67,000+ political comments** across 150+ questions in German, French, and Italian, annotated for stance. Useful for multilingual brand opinion monitoring.
**URL:** https://huggingface.co/datasets/ZurichNLP/x_stance

---

## Named entity recognition for brands and products

**103. WNUT 2017 Emerging Entities**
NER dataset with 6 entity classes including **"product" and "corporation"**—designed for emerging entities not well-covered by standard NER. Useful for brand/product extraction from marketing text.
**URL:** http://nlpprogress.com/english/named_entity_recognition.html

**104. Best Buy E-Commerce NER Dataset (Kaggle)**
Named entity recognition dataset from Best Buy e-commerce queries, annotated for product-related entities.
**URL:** https://www.kaggle.com/datasets/debasisdotcom/name-entity-recognition-ner-dataset

---

## How to prioritize these datasets for fine-tuning

Not all 104 datasets carry equal weight for building a sales and marketing AI. The highest-impact datasets fall into three tiers based on their direct relevance to generating persuasive, conversion-oriented text.

**Tier 1 — Direct fine-tuning material** includes the sales conversation datasets (#1–5), persuasion corpora (#14–18), ad copy generation sets (#32–37), and the copywriting dataset (#66). These contain the exact input-output patterns needed for an instruction-tuned sales AI.

**Tier 2 — Knowledge enrichment** covers the negotiation dialogues (#10–13), argument mining data (#19–20), headline/slogan datasets (#58–62), and product description corpora (#63–65). These teach the model about persuasive structure, creative language, and product positioning.

**Tier 3 — Contextual understanding** encompasses the sentiment analysis datasets (#84–97), consumer behavior data (#68–79), and advertising performance datasets (#26–57). These don't directly generate sales copy but provide the model with deep contextual knowledge about what customers care about, how they behave, and what drives conversions.

## Conclusion

This collection of **104 datasets** provides comprehensive coverage for fine-tuning an AI across the full sales and marketing stack. The most unique and underutilized finds are the **Anthropic Persuasion dataset** (#15) for measuring persuasive effectiveness, the **CaSiNo negotiation corpus** (#11) with per-utterance strategy annotations, and the **SemEval propaganda detection dataset** (#16) which teaches the model to recognize and deploy 18 distinct influence techniques. For maximum fine-tuning impact, combine the instruction-formatted sales conversations with the persuasion strategy corpora and ad copy datasets, then enrich with sentiment and consumer behavior data to ground the model's outputs in real customer psychology.