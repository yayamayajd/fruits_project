fruits_project start

Plan:


DB:Postgres

Backend:Python+Flask

Frotend: HTML+JINJA2

Test: Pytest

CI/CD:Github actions

Deployment: Microk8S/minikube on VM ubuntu on home NAS in local network 





Dev log:

2025.02.02

DB has built
models.py has been added
on process of backend API...

2025.02.07

modified all endpoint as close as 'RESTFul'
add the to_dict func to all endpint Class

2025.2.10

Successfully linked the comment feature on the fruit detail page to users.
But released that the endpoint can't be RESTFUL becase I use reder template instead return json data. But to catch json I need to use JS to write fronten.
So I move to the task 'all endpints should be RESTFUL to V2.0', add study plan for JS after V1.0 deployed

2025.2.12

Checked the home NAS and deployment environment; the hardware supports virtual machines, and the memory is sufficient for MicroK8s.
Suddenly noticed log warnings—detected signs of DDoS attacks and something resembling SQL injection.
Shut down the server for inspection. After scanning all ports, found two unknown ports with no identifiable bound processes, and they couldn't be terminated with standard commands.
Since it was too late, decided to sleep first and investigate later.

2025.2.13

Enhanced NAS security measures, reconfigured the static IP address, and performed a full system scan.
On the router, disabled unnecessary features like AI-Cloud, reviewed all port forwarding rules, and found that the strange port 7788 had finally closed.
With security concerns addressed, decided to return to API development and adjustments.



2025.2.15

Give uo the directory related to the Place table in version 1.0 and moved it to a later version.
Spent a long time adjusting the relationship definitions between tables. Initially, I took a shortcut by using backref, but this resulted in countless SAWarning messages. However, as the relationships became more complex, backref was no longer sufficient.
The difference between backref and back_populates is that the former requires definition on only one side and automatically creates the reverse relationship, while the latter must be manually defined on both sides.






📌 Challenges Encountered in Backend, Frontend, and Database Development📌 


Database

Since the school instructors focused on teaching how to design databases and tables, the design phase was completed fairly quickly.



Backend API

Also developed using the Python Flask framework, but this time integrated with a database, which led to learning about ORM and data modeling using SQLAlchemy.
In previous school projects, the endpoint requirements were provided by the instructors, and the number of endpoints was relatively small, so there were no major difficulties.
However, this time, the project required designing endpoints, database structures, and relationship mappings based on self-defined requirements.
This felt like running blindfolded—I thought I had a good grasp theoretically, but in practice, I encountered many specific issues.
For example, school assignments did not involve ORM or how to use relationship tables to integrate objects and call them based on requirements. Debugging in these areas took a significant amount of time.



Frontend

The initial HTML pages were too ugly, and the "client" rejected them.
Eventually, the "client" took matters into their own hands and wrote a CSS template.



Other Issues

Got too focused on development and forgot to eat and sleep. 😅
