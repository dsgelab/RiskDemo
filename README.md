## GPT Demo

### Setup
```bash
git clone https://github.com/dsgelab/RiskDemo.git
cd RiskDemo
pip3 install -r requirements.txt
python3 main.py
```
- A finngen-risteys vm is a must. To tunnel the database Risteys is using, ssh -NL port:database_IP_addr:port username@vm_external_IP. 

- A Q&A demo for users to get a database query, simple python code to calculate disease risk when they ask a question such as "If I have disease A and I am a guy at 45, what is my risk of having disease B?". Users can obtain the risk calculated by the machine at the same time.


- Comparisons among the results using different engines

questions | answers	| davinci | curie | babbage | ada
--------- | ------- | ------- | ----- | ------- | ---
What is my risk of angina if I am a female with a history of heart attack? | ['heart attack', 'angina', 'na', 'female] | ['heart attack', 'angina', 'na', 'female] | ['heart attack', 'angina', 'na', 'female] | ['heart attack', 'angina', 'female', 'na'] | ['heart attack', 'angina', 'na', 'female']
What's the risk of having cancer if I have heart attavk? | ['heart attack', 'cancer', 'na', 'na'] | ['cancer', 'heart attack', 'na', 'na'] | ['heart attack', 'cancer', 'na', 'na'] | ['cancer', 'heart attavk', 'na', 'na'] | ['heart attavk', 'cancer', 'na', 'na']
If I am a girl at 24 with cancer, what's my risk of having diabeties? | ['cancer', 'diabetes', '24', 'female'] | ['cancer', 'diabetes', '24', 'female'] | ['cancer', 'diabeties', '24', 'female'] | ['cancer', 'diabetes', '24', 'female'] | ['cancer', 'diabeties', 'na', 'na']
I am a 65-year-old male. I had strke. What is my risk of epilepsy? | ['stroke', 'epilepsy', '65', 'male'] | ['stroke', 'epilepsy', '65', 'male'] | ['stroke', 'epilepsy', '65', 'male'] | ['epilepsy', 'stroke', '65', 'male'] | ['epilepsy', 'stroke', 'na', 'na']
I am 20 and I have cancer | ['cancer', '20', 'na', 'na'] | ['cancer', '20', 'na'] | ['cancer', '20', 'na'] | ['cancer', 'na', '20', 'female'] | ['cancer', '20', 'male']
