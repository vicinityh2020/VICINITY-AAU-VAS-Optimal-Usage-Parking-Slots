# VICINITY-AAU-VAS-Optimal-Usage-Parking-Slots
This documentation describes the adapter of AAU VAS - Optimal Usage_Parking Slots.

# Infrastructure overview

Parking slot usage data is collected through VICINITY by using three parking sensors to achieve monitoring function. A residential microgrid, which consists of PV, wind turbine and battery, is emulated in AAU IoT-microgrid Lab. The residential microgrid is assumed to supply power to EV chargers in the three parking slots. The real-time charging price is calculated by considering the simulated real-time utility electricity price, state-of-charge of batteries, and forecasts of the PV and wind turbine power generation. The parking slot usage and the real-time charging price will be sent automatically to users after subscribing Optimal Usage of Parking Slots by Considering Energy Costs VAS.

Adapter serves as the interface between VICINITY and LabVIEW enabling to use all required interaction patterns.

![Image text](https://github.com/YajuanGuan/pics/blob/master/%E5%9B%BE%E7%89%871.png)

# Configuration and deployment

Adapter runs on Python 3.6.

# Adapter changelog by version
Adapter releases are as aau_adapter_x.y.z.py

## 0.0.1
Start version, it works with agent-service-full-0.6.3.jar, and it receives three parking slot usage states and publishes an event with vacant parking slot account and real-time EV charging price.

# Functionality and API

## Publish an event to the subscribers. 
### Endpoint:
            PUT /objects/{oid}/events/{eid}
Publish the vacant parking slot number, EV charging price and current time. Users can receive the number of free parking slot and charging price automatically.
### Return:
After subscribing the VAS successfully, the subscriber receives a response for instance:  
{  
    "value": "3.15",  
    "free": "2",  
    "time": "2018-11-10"  
}
