# VICINITY-AAU-VAS-Optimal-Usage-Parking-Slots
This documentation describes the adapter of AAU VAS - Optimal Usage_Parking Slots which provides users with data about the numbers of free parking slot and the real-time charging price for EVs in order to optimize energy and parking slot usages and to reduce end-users’ bills.

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

## Read residential microgrid operation states
### Endpoint:
            GET /remote/objects/{oid}/properties/{pid}
Return last known value and time received by the VAS. The “oid” is UUID of the VAS and “pid” is a property identifier. Users can read generated active power outputs of PV and WT, the SoC of batteries, and active power consumption of the microgrid.

## Subscribe to event channel
### Endpoint:
            POST /objects/{oid}/events/{eid}
Return last vacant parking slot account, EV charging price and time received by the VAS. The “oid” is UUID of the VAS and “eid” is a event identifier. Users can receive the number of free parking slot and charging price automatically.
