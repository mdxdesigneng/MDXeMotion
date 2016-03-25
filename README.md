# MDXeMotion Platform Software

This software provides a gateway between data sources (typically motion simulators) and motion platforms such as the Middlesex University Pneumatic Stewart Platform

- **PlatformEffector** contains code to connect to a physical platform
- **clients** provide modules to receive data from motion simulators and provide normalized inputs to the middleware
- **PlatformMiddleware** receives data from a client and produces the translation and rotation data needed to drive a physical platform. This code provides the capability to adjust the gain and washout for each of six degrees of freedom of motion 

