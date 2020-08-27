# Network-Audio-Simulation

- **Description** : Simulation of Audio packets sent over the network and approaches to alleviate common network errors. A series 
of simulations replicating bad network conditions (probability of loss) with different packet sizes. The goal is to try different methods 
to deal with the lack of audio packets during live audio playback (like a VoIP call) and find which works best. Some of these attempts at a solution include: 

1. Replaying the last received audio packet for the entire duration of lost packet.
2. Replaying the last sample of the last received packet for the entire duration of lost packet.
3. Complete silence for the duration of lost packet.
___
- **Relevant Area** : Computer Networking.
___
- **Tools / Platforms**:  Python, Sunau library.
___

