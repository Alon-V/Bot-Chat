# Welcome to our network traffic (Wireshark) 🦈 tour

## First of all I will show you the 3 types of Handshakes we have
### 1. Our Launcher frequently connects just to check if the server is online and then immediately disconnects.

This includes:

`SYN` : A reqst to connect

  ⤵️
  
`ACK` : An ackolgemnet (a yes/no answer to the reqst) and if its accpteed then the coneection happans otherwise nothing happens

  ⤵️
  
`FIN` : end connection
<div align="center">
<img width="1215" height="96" alt="image" src="https://github.com/user-attachments/assets/d0db2a95-8838-496c-b7ba-3f81365dc77a" />
  </div>

### 2. The "Observer" is a hidden connection to the Launcher that is keepet open to update the user list.

This includes:

`SYN` : A reqst to connect

  ⤵️
  
`ACK` : An ackolgemnet (a yes/no answer to the reqst) and if its accpteed then the coneection happans otherwise nothing happens
an easy way to find him is to look at the Length, it wont be longer then 25 bytes becose the massgae its sends is: __LAUNCHER__

### 3. A "New User"
This includes:

`SYN` : A reqst to connect

  ⤵️
  
`ACK` : An ackolgemnet (a yes/no answer to the reqst) and if its accpteed then the coneection happans otherwise nothing happens
The massage in this one is the name of the user

Here you can see the Handshak made to create a new user and the massage sent that include the user name of the new user
<div align="center">
<img width="1347" height="68" alt="image" src="https://github.com/user-attachments/assets/d880ce11-c009-4b6f-b4be-73d914a188ed" />
  </div>
<div align="center">
<img width="1107" height="668" alt="image" src="https://github.com/user-attachments/assets/8def7304-51b1-4f84-817e-87307202e186" />
  </div>
the difrennce in source and destination IP shows that the user was crated not in the same pc that the server is running on
you also get the randomized port that the user is got, when sent a reqest to the server thats running on port 8081

## Sending a massage
When sending a massage it will look like this
<div align="center">
<img width="1049" height="17" alt="image" src="https://github.com/user-attachments/assets/e0005833-ace6-4880-9397-f55beced01ae" />
  </div>
You can see the the source ip of massage in this case `10.0.0.15` and the desttnion (its always the server location) in this case `10.0.0.16`.
and the port of the user and server.

and this is the massage that was send
<div align="center">
<img width="907" height="427" alt="image" src="https://github.com/user-attachments/assets/6420c41c-6564-4fee-be6c-cae4b625bf73" />
</div>

## Reciving a massage
Becose the massage is a broadcast so the server sents this massage to all useres that are coneccted (you can see that the ports are diffrent)
<div align="center">
<img width="1072" height="49" alt="image" src="https://github.com/user-attachments/assets/c7e77c29-5ee5-4e25-8e6b-2d70261104ae" />
</div>
In case its a praivet massage then he sends this onnly to one user



