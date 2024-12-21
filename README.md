# Project e-sight

## 1. Project description

My 21/12-24 idea is to improve the ability to detect people around my car. A Volvo v70 mk2 2009. I have no visual of any way. However, I could do something with my phone as a PoC.

### 1.1 Definition of done

Definition of done for this project is reaching a decisive answer if this is possible without too much work. We swore to abide by simplicity as simplicity will let us make this scalable. Focus on that.

The ultimate goal is to improve indication of objects in real-time if there are obstacles, main target for this project are humans.

Good luck.

### 1.2 Planning phase

#### 1.2.1 What do we want?

This is the requirements for the project:
* We want to see the following objects ["Humans"]
* This should be visually enhanced

## 2. Project Phases

### Phase 1: Planning and Requirements Gathering

**Objective:** Detect humans around your car at night using available resources.

**Resources:**
- 1x Raspberry Pi 3B+
- 1x HC-SR501 PIR motion sensor
- Your smartphone

The HC-SR501 PIR motion sensor is a low-power consumption, indoor use sensor that can detect motion in a wide field of view (less than 100 degrees). It has an adjustable delay time between 0.5-200 seconds, which allows for customization of the sensor's sensitivity. The sensor can be powered by a 5V source such as a Raspberry Pi.

**Constraints:**
- Budget-friendly
- Time-limited
- Simple and scalable solution

### Phase 2: Technical Approach

**HC-SR501 PIR motion sensor:**
- Use the sensor to detect motion in the vicinity of the car.
- Mount the sensor strategically on the car to maximize coverage.

**Raspberry Pi:**
- One Raspberry Pi can be used to process data from the sensor.
- The Raspberry Pi can handle communication with your smartphone for real-time alerts.

**Smartphone Integration:**
- Develop a simple app or use existing tools to receive and display alerts from the Raspberry Pi.
- The app should indicate the direction of the detected human.

### Phase 3: Implementation Steps

**Hardware Setup:**
- Connect the HC-SR501 PIR motion sensor to the Raspberry Pi.
- Ensure the sensor is properly calibrated and positioned.

**Software Development:**
- Write a script on the Raspberry Pi to process sensor data and detect human-like motion.
- Implement a communication protocol (e.g., MQTT) between the Raspberry Pi and the smartphone.
- Develop a basic smartphone app to receive and display alerts.

**Testing and Validation:**
- Test the setup in various nighttime conditions to ensure reliability.
- Fine-tune the sensor placement and software parameters for optimal performance.

### Phase 4: Proof of Concept (PoC)

**Initial Testing:**
- Conduct initial tests in a controlled environment to validate the detection and alert system.
- Document findings and make necessary adjustments.

**Real-World Testing:**
- Test the system in real-world conditions around your car.

### Phase 5: Documentation and Review

**Documentation:**
- Create detailed documentation of the setup, code, and testing results.
- Include any challenges faced and solutions implemented.

**Review:**
- Review the project against the definition of done.
- Assess the scalability and potential for future enhancements.

## 3. Next Steps

**Hardware Acquisition:**
- Ensure you have all the necessary hardware components.
- If additional sensors or components are needed, identify budget-friendly options.

**Software Development:**
- Begin writing the scripts for the Raspberry Pi.
- Research and select a suitable communication protocol.

**App Development:**
- Choose a development platform for the smartphone app.
- Start designing the user interface and functionality.


## 4. Risks and Mitigation Strategies

**Risk:** Inaccurate sensor readings due to environmental factors.
**Mitigation:** Implement calibration procedures and fine-tune sensor placement. Use multiple sensors for redundancy and data validation.
**Risk:** False positives or negatives leading to unsafe driving conditions.
**Mitigation:** Implement a machine learning algorithm to improve the accuracy of the detection system. Continuously update and refine the algorithm based on real-world data.
**Risk:** Limited battery life on the Raspberry Pi.
**mitigation** Not a problem as the 12V battery will be used to power the Raspberry Pi.
**Risk:** Delays in hardware acquisition or software development.
**Mitigation:** Maintain a realistic project schedule and allocate sufficient time for each task. Break down larger tasks into smaller, manageable sub-tasks.

## 5. Project Schedule
This project will be completed before the sixth of january 2025. This is the day of the 21 dec 2024.
**Week 1-2:** Hardware acquisition and research.
**Week 3-4:** Sensor calibration and integration with the Raspberry Pi.
**Week 5-6:** Development of the communication protocol and initial testing.
**Week 7-8:** Smartphone app development and user interface design.
**Week 9-10:** Integration of the smartphone app with the Raspberry Pi and final testing.
**Week 11:** Documentation and presentation preparation.