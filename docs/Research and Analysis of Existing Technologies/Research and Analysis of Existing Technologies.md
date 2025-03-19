## Research and Analysis of Existing Technologies

# 1. Problem Definition and Scope

  The goal of Planterbox is to create an AI-powered mobile application that helps users identify plants, provide care instructions, track plant growth, and offer gardening recommendations. 
  
  The research aims to address the following problems:
  - Accurate plant identification using image recognition.
  - Generating personalized care instructions based on plant species and environmental conditions.
  - Tracking plant growth and providing insights to improve gardening skills.
  - Continually training an ML model that we develop.

  The application targets plant enthusiasts, beginner gardeners, and botanists who need a reliable tool to identify plants, learn about their care, and track their progress. The significance lies in making plant care accessible and enjoyable for everyone with the help of technology. Providing the typical member of the household the ability to nurture and care for their plants is the goal of Planterbox.

  The research will focus on:
  - AI-powered plant identification using image recognition.
  - Data collection and preprocessing for training the AI model.
  - Integration of care instructions and lifecycle information.
  - Development of a growth tracking system and gardening recommendations.

  Limitations:
  - Mainly focusing on common house plant species.
  - Potential to run into financial complications when the app is deployed
  - Ability to chart and document growth stages

# 2. Project Division into Subtasks

  **Subtask 1: Data Collection and Preprocessing**
  
  **Description:**
  Collect and preprocess a high-quality dataset of plant images and associated metadata. This dataset will be used to train the AI model for plant identification and care recommendations.
  We will ensure that the data processed is first limited in its scope so as to not train our model with uncommon household plants (ie, Carrots and potatoes).
  
  **Relevance:**
  The accuracy of the AI model depends on the quality and diversity of the dataset. Proper preprocessing ensures the data is clean, labeled, and ready for training.

  **Subtask 2: AI Model Development and Evaluation**
   
  **Description:**
  Develop an AI model for plant identification using image recognition. Evaluate the model's performance and fine-tune it for accuracy and efficiency.
  
  **Relevance:**
  The AI model is the core of the application, allowing users to identify plants and receive care instructions. Its performance will impacts user satisfaction.

   
## 3. Research Exisiting Technologies and Methodologies

###**Subtask 1: [Datasets](https://github.com/Chromium99/Planterbox/blob/main/docs/Datasets/Dataset%20Links%20and%20Descriptions.md)**

  **1. [House Plant Image Classification Dataset](https://images.cv/dataset/house-plant-image-classification-dataset)**
  **Strengths:**
  - Focused specifically on house plants.
  - Labeled images for plant identification.
  **Weaknesses:**
  - Limited diversity in plant species.
  **Applicabilty:**
  - Initial development and testing of models.
  
  **2. [Open Plant Image Archive (OPIA)](https://ngdc.cncb.ac.cn/opia/datasets)**
  **Strengths:**
  - Contains a wide variety of differnet plant species.
  - High-quality images with detailed metadata.
  **Weaknesses:**
  - May require significant preprocessing.
  **Applicabilty:**
  - Disease detection of plants.
    
  **3. [Pl@ntNet-300K Dataset](https://zenodo.org/records/5645731#.Yuehg3ZBxPY)**
  **Strengths:**
  - Large and diverse plant images datasets.
  - Ideal for identifying differnet plant species.
  **Weaknesses:**
  - Mainly focuses only on plant identification.
  **Applicabilty:**
  - Training a plant identification model.
    
###**Subtask 2: **
   
## 4. Reproducible Sources
