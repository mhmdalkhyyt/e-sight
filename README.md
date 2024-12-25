---
title: Project e-sight
by: Muhammed Al Khayyat
date: 2024-12-21
output: pdf_document
---

# Project e-sight

## 1. Project description

### 1.1 Objective

The main idea is to improve the ability to detect people around my car using a camera-based object detection system. The focus will be on humans. The Head-Up Display (HUD) will now be an addressable LED strip from Luxor, with a length of 1m and 60 LEDs. A camera will also be installed onboard.

Improve the ability to detect people around my car using a camera-based object detection system. Focus on humans. Use a Luxor LED strip (1m, 60 LEDs) for Head-Up Display (HUD).
### 1.2 Definition of done

Definition of done for this project is reaching a decisive answer if this is possible without too much work. We swore to abide by simplicity as simplicity will let us make this scalable. The ultimate goal is to improve indication of objects in real-time if there are obstacles, with the main target for this project being humans.
Reach a decisive answer if this is possible without too much work. Aim for simplicity for scalability. Goal is to improve indication of objects in real-time, with a main target for this project being humans.

## 2. Project Phases

### 2.1 Planning and Requirements Gathering

- **Objective:** Detect humans around your car at night using available resources.
- **Resources:**
  - 1x Raspberry Pi 3B+
  - 1x Camera module
  - 1x Addressable LED strip from Luxor (1m, 60 LEDs)
  - Jumper cables
- **Constraints:**
  - Budget-friendly
  - Time-limited
  - Simple and scalable solution

- Detect humans around your car at night using available resources.
- Raspberry Pi 3B+, camera module, Luxor LED strip (1m, 60 LEDs), jumper cables.
- Budget-friendly, time-limited, simple and scalable solution.
### 2.2 Technical Approach

- **Camera-based Object Detection:** Use the installed camera module to capture images of the surrounding area. Implement a machine learning model to detect human-like objects in the images.
- **Raspberry Pi and LED Strip:** Connect the addressable LED strip from Luxor to the Raspberry Pi. Develop a script to control the LED strip based on the x-axis position of the detected objects.
- Camera-based Object Detection: Use camera module for image capture, implement machine learning model for human-like object detection.
- Raspberry Pi and LED Strip: Connect Luxor LED strip to Raspberry Pi. Develop script to control LED strip based on x-axis position of detected objects.

### 2.3 Implementation Steps

- **Hardware Setup:** Connect the camera module and addressable LED strip from Luxor to the Raspberry Pi.
- **Software Development:** Train a machine learning model to detect human-like objects in images. Write a script on the Raspberry Pi to process camera data and control the LED strip based on the detected objects' positions.
- **Testing and Validation:** Test the setup in various nighttime conditions to ensure reliability. Fine-tune the camera placement and software parameters for optimal performance.
- Hardware Setup: Connect camera module and Luxor LED strip to Raspberry Pi.
- Software Development: Train machine learning model for human-like object detection in images. Write script for Raspberry Pi to process camera data and control LED strip.
- Testing and Validation: Test setup in various nighttime conditions, fine-tune camera placement and software parameters.

### 2.4 Proof of Concept (PoC)

- Conduct initial tests in a controlled environment to validate the detection and indication system.
- Test the system in real-world conditions around your car.
- Initial tests in controlled environment to validate detection and indication system.
- Test system in real-world conditions around your car.

### 2.5 Documentation and Review

- Create detailed documentation of the setup, code, and testing results.
- Review the project against the definition of done. Assess the scalability and potential for future enhancements.
- Create detailed documentation of setup, code, and testing results.
- Review project against definition of done, assess scalability and potential for future enhancements.

## 3. Next Steps

- **Hardware Acquisition:** Ensure you have all the necessary hardware components.
- **Software Development:** Begin training the machine learning model. Begin writing the scripts for the Raspberry Pi.
- **Hardware Integration:** Start integrating the camera module and addressable LED strip from Luxor with the Raspberry Pi.
- Hardware Acquisition: Ensure necessary hardware components.
- Software Development: Begin training machine learning model, begin writing scripts for Raspberry Pi.
- Hardware Integration: Start integrating camera module and Luxor LED strip with Raspberry Pi.

## 4. Risks and Mitigation Strategies

- **Risk:** Inaccurate object detection due to environmental factors or camera quality.
  - **Mitigation:** Use a high-quality camera module and implement post-processing techniques to enhance accuracy. Continuously update and refine the machine learning model based on real-world data.
- **Risk:** False positives or negatives leading to unsafe driving conditions.
  - **Mitigation:** Implement a machine learning algorithm to improve the accuracy of the detection system. Continuously update and refine the algorithm based on real-world data.
- **Risk:** Limited battery life on the Raspberry Pi.
  - **Mitigation:** Utilize a 12V battery to power the Raspberry Pi, ensuring sufficient power for the duration of the project.
- **Risk:** Delays in hardware acquisition or software development.
  - **Mitigation:** Maintain a realistic project schedule and allocate sufficient time for each task. Break down larger tasks into smaller, manageable sub-tasks to minimize delays and ensure timely completion.
- Risk: Inaccurate object detection due to environmental factors or camera quality.
  - Mitigation: Use high-quality camera module, implement post-processing techniques to enhance accuracy. Continuously update and refine machine learning model.
- Risk: False positives or negatives leading to unsafe driving conditions.
  - Mitigation: Implement machine learning algorithm to improve accuracy. Continuously update and refine algorithm based on real-world data.
- Risk: Limited battery life on Raspberry Pi.
  - Mitigation: Utilize 12V battery to power Raspberry Pi.
- Risk: Delays in hardware acquisition or software development.
  - Mitigation: Maintain realistic project schedule, allocate time for each task. Break down larger tasks into smaller, manageable sub-tasks.

## 5. Project Schedule

- This project will be completed before the sixth of January 2025.
- **Week 1-2:** Hardware acquisition and research.
- **Week 3-4:** Camera calibration and integration with the Raspberry Pi.
- **Week 5-6:** Machine learning model training and initial testing.
- **Week 7-8:** Development and integration of the LED strip with the Raspberry Pi.
- **Week 9-10:** Final testing and validation of the system.
- **Week 11:** Documentation and presentation preparation.
- Completion before January 6, 2025.
- Week 1-2: Hardware acquisition and research.
- Week 3-4: Camera calibration and integration with Raspberry Pi.
- Week 5-6: Machine learning model training and initial testing.
- Week 7-8: Development and integration of LED strip with Raspberry Pi.
- Week 9-10: Final testing and validation of the system.
- Week 11: Documentation and presentation preparation.

## 6. Git Remote Command
