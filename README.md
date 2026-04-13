Blood Group Detection Using Image Processing and Machine Learning
Authors:
B.Anjali (Y22ACS421)
D.Vyshnavi (Y22ACS444)
K.Harsha Vardhan (Y21ACS476)
B.Mahesh (Y22ACS423)
Implementation
Web Application
Flask-based web application for blood group detection from images.
🔗 https://github.com/Anjali16301/blood-scan-website
Live Website
Blood group detection system deployed and accessible publicly.
🌐 https://blood-scan-websites.onrender.com
Overview
Blood Group Detection is an AI-powered medical image classification system designed to automatically detect blood groups from dataset images using deep learning and image processing techniques.
The system processes blood group images through a multi-stage preprocessing pipeline, extracts visual features using a  Convolutional Neural Network, and classifies all 8 blood group types (A+, A-, B+, B-, AB+, AB-, O+, O-) with 96.4% accuracy — no physical blood samples required.
The platform also provides a web interface where users can upload blood group images and receive instant automated predictions.
Project Components
1. Image Preprocessing Pipeline

Resizes input images to 224×224 pixels
Applies CLAHE contrast enhancement
Performs Gaussian blur for noise removal
Normalizes pixel values to [0, 1] range
Converts images to CNN-ready tensors

2. Deep Learning Classifier (ResNet50)

Uses ResNet50 pretrained on ImageNet (Transfer Learning)
Custom classification head with Dense layers and Dropout
Two-phase fine-tuning strategy for blood group images
Handles all 8 blood group categories
Outputs predicted label with confidence score

3. Data Augmentation Module

Random rotation, flipping, zoom, brightness adjustment
Minority class oversampling for class balance
Class-weighted loss computation
Prevents overfitting and improves generalization

4. Flask Web Application

Upload blood group images via browser
Displays predicted blood group and confidence score
User registration and login system
REST API for image classification
Deployed live on Render platform


System Architecture:
The Blood Group Detection system integrates multiple components including the Image Preprocessing Pipeline, ResNet50 CNN Classifier, Data Augmentation Module, Flask Web Server, SQLite Database, and a Public Web Interface.
These components work together to automate blood group classification and deliver instant predictions to users through a web browser.

Technologies Used:
Backend
Python 3.x
TensorFlow / Keras
OpenCV (Image Processing)
Flask (Web Framework)
SQLite (Database)
scikit-learn

Deep Learning
CNN (Convolutional Neural Network)
ImageDataGenerator (Augmentation)
Frontend:
HTML5
CSS3
JavaScript
Key Features:
AI-based blood group classification from images
Non-invasive — no physical blood samples needed
Supports all 8 blood group types (ABO + Rh factor)
96.4% classification accuracy on test dataset
Real-time predictions through web interface
Data augmentation for improved generalization
Class imbalance handling for rare blood groups
Confidence score display for each prediction
Batch image processing support
Cross-platform web accessibility
Research Contribution:
This project demonstrates how Artificial Intelligence and Computer Vision can improve medical diagnostics by automatically classifying blood groups from digital images without requiring invasive blood sample collection or laboratory chemicals.
The system achieves 96.4% accuracy using CNN Transfer Learning and establishing a foundation for AI-powered non-invasive medical diagnostics.
Department of Computer Science and Engineering
Bapatla Engineering College
Future Work:
Integration with Electronic Health Record (EHR) systems
Mobile application development (Android and iOS)
Federated learning for privacy-preserving model training
Multilingual support for diverse user communities
Support for rare blood group antigen systems
Web-based administrative dashboard
GitHub Repository:
The source code for the Blood Group Detection system is available at:
Web Application & Backend
Flask web application, ML model, and deployment configuration.
🔗 https://github.com/Anjali16301/blood-scan-website
Project Documentation:
Full project thesis with diagrams, analysis, and implementation details.
Live Demo
🌐 https://blood-scan-websites.onrender.com





