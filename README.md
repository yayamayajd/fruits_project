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



2025.2.17

Started writing tests and setting up the necessary environment.
I discovered an issue: while the NAS has enough memory, the CPU is way too old. This means I have to push its limited performance to the extreme. (I really miss the time when I could do whatever I wanted during my free trial on Azure.)

So, I decided to install the minimal version of Ubuntu Server and configured it with a static IP.
At the same time, I give uo that using a pipeline to build images directly on the VM. Instead, I plan a alternative approach that is building the images on my loptop/or github sever(neend to figure out the way), pushing them to a Docker registry, and letting Kubernetes on the VM pull and deploy them.



2025.2.18

After setting up the VM, I ran into issues right on the first update attempt—it couldn’t connect to remote servers.
The IP and gateway configurations were correct, so I tried ping—only to realize that the mini version of the system didn’t have ping installed. I then tried apt, but it resulted in a dead loop because it couldn't reach remote servers.

Next, I attempted curl google.com and found that DNS resolution wasn’t working, though I could connect using an IP address.
After some investigation, I realized that the DNS nameserver wasn’t properly configured. I tried manually modifying /etc/resolv.conf using nano or vi, only to find out that neither nano nor vi were installed.

In the end, I updated the nameserver using echo, and the update finally succeeded... but I celebrated too soon.

After a reboot, the changes were lost because /etc/resolv.conf turned out to be a symlink. I had to delete the file, recreate it, and manually write in the nameserver. (Later, while installing Kubernetes, I ran into another DNS restriction issue with Google’s DNS and had to go through another round of trial and error before finally succeeding with Cloudflare’s DNS.)

Once again, I found myself missing the seamless cloud environment. LOL

Anyway, MicroK8s (the lightweight version) is now installed. I tested it with Nginx (and picked up some extra Nginx knowledge along the way), and everything works fine. Just need to install Docker for deployment, and that should be about it! 



February 20, 2025

While writing tests, I found several key features related to reviews and user-fruit_list were missing, so I had to go back and fill in the gaps... I feel like my brain is running out of power 😭 not a good feeling that having to rework things halfway through testing! Lesson learned: if you underestimate the desgin part, then you'll end up with endless technical debt. But it's also frustrating when I suddenly get new ideas during development and want to make database-level changes...

I think learning JavaScript has become an urgent priority now. If I continue adding new features and relationships in the future, not following RESTful principles might cause big problems. 😂





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
