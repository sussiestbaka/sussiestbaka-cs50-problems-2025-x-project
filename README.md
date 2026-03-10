# AUTOFACE

#### Video Demo: [https://youtu.be/x6YSxoBDbuw]

#### Description:


AUTOFACE is a cutting-edge car security system designed to significantly reduce the risk of vehicle theft by integrating advanced facial recognition technology with hardware control of the car’s ignition system. At the heart of the project is the Khadas VIM3 single-board computer, a powerful and compact device capable of running sophisticated AI models and managing real-time hardware interactions through its GPIO pins.

The core functionality of AUTOFACE revolves around its ability to distinguish between authorized and unauthorized users. When the onboard camera captures an image of the person attempting to start the car, the system uses state-of-the-art facial recognition models-specifically **SFace** and **Yunet**-to analyze and verify the identity.

- **Yunet** is a face detection model that locates faces within an image or video frame. It uses advanced computer vision techniques to quickly and accurately identify the presence and position of faces, even in complex scenes or with partial occlusions. Yunet helps the system find faces before further analysis.

- **SFace** is a deep learning-based face recognition model designed to efficiently extract distinctive facial features from detected faces. It processes the detected face to generate a unique numerical representation (faceprint) that captures key facial landmarks and characteristics. This allows for precise matching against stored authorized faces, even under varying lighting conditions or angles.

If the detected face matches one of the authorized profiles stored in the system, the Khadas VIM3 activates the car ignition relay via GPIO, allowing the engine to start seamlessly.

In contrast, if the system identifies an unfamiliar face, it triggers an immediate security response by sending a WhatsApp alert to the car owner through the PyWA library. This alert includes relevant information and images, enabling the owner to take swift action in case of a potential theft attempt. This real-time notification system enhances security by providing instant awareness of unauthorized access attempts.

AUTOFACE also offers a rich web-based interface that empowers the user with full control and monitoring capabilities. Through this secure webserver, users can:

- Log in safely with authentication
- Access a live camera preview to monitor the vehicle remotely
- Manually capture and send photos to WhatsApp for additional verification
- Manage the facial database by adding or removing authorized faces via a file manager
- Log out securely to protect access

This interface ensures a user-friendly experience while maintaining high security standards.

The software stack is built primarily in Python, leveraging a suite of robust libraries and frameworks to deliver reliable performance. Key dependencies include Flask for the webserver, OpenCV and NumPy for image processing and numerical computations, Flask-SQLAlchemy for database management, and python-dotenv for environment configuration. The project also integrates pywa for WhatsApp messaging and Requests for HTTP communications, ensuring smooth interaction with external services.

To deploy AUTOFACE, users first install a Linux operating system on the Khadas VIM3 board, followed by Python 3.11 and all necessary Python modules listed in the `all_modules_installed_in_os.txt` file. This setup ensures that the device is fully equipped to run the facial recognition models and handle GPIO-based relay control efficiently.

Maintained by me (SUSSIESTBAKA), AUTOFACE currently does not specify a license but stands as a practical demonstration of edge AI applications in automotive security. By combining hardware control, AI-driven facial recognition, and instant communication, AUTOFACE provides a comprehensive and modern approach to safeguarding vehicles against theft, making it a valuable tool for car owners seeking advanced protection.