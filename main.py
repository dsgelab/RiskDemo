import openai
import uuid, re
import pandas as pd
from fuzzywuzzy import process
from gpt import GPT, Example
from flask import Flask, request, jsonify
# import data_process
# import os
# import sys
# sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
# import datefinder
# from data import DataProcessor
import json
# import pickle

app = Flask(__name__, static_url_path='')

# global noteData
# global cancerData
# global ptData
# session_dict = {'is_data_processed': False}
global gpt

openai.api_key = "sk-MKxaEJsHbFyW5U7bP2e0d2B9mzpoAxuWQ73sDmo2"

gpt = GPT(engine="davinci",
          temperature=0,
          max_tokens=300,
          input_prefix="Q: ",
          input_suffix="(q_end)",
          output_prefix="A: ",
          output_suffix="(a_end)",
          append_output_prefix_to_query=True)

# gpt.add_example(
#     Example('I am a 53-year-old woman with a history of stroke. What is my risk of having angina?',
#             '''
#             df = pd.read_sql_query("SELECT * FROM all_coxhrs WHERE prior = 'stroke' AND outcome = 'angina' AND lag_hr IS NULL;", engine)
#             d = dict(zip(df.keys(),df.values[0]))
#             np.exp(-d['bch'] * np.exp(np.dot(
#                 lifelines.utils.normalize(np.array([datetime.datetime.today().year - 53, True, 1]),
#                                       np.array([d['year_norm_mean'],d['prior_norm_mean'],d['sex_norm_mean']]),
#                                       std=1),
#                 np.array([d['year_coef'], d['prior_coef'], d['sex_coef']])
#             )))
#             '''))
# gpt.add_example(
#     Example('What is my risk of angina if I am a female at 33 with a history of heart attack?',
#             '''
#             df = pd.read_sql_query("SELECT * FROM all_coxhrs WHERE prior = 'heart attack' AND outcome = 'angina' AND lag_hr IS NULL;", engine)
#             d = dict(zip(df.keys(),df.values[0]))
#             np.exp(-d['bch'] * np.exp(np.dot(
#                 lifelines.utils.normalize(np.array([datetime.datetime.today().year - 33, True, 1]),
#                                       np.array([d['year_norm_mean'],d['prior_norm_mean'],d['sex_norm_mean']]),
#                                       std=1),
#                 np.array([d['year_coef'], d['prior_coef'], d['sex_coef']])
#             )))
#             '''))
# gpt.add_example(
#     Example('I am a 78-year-old man with angina. What is my risk of having heart failure?',
#             '''
#             df = pd.read_sql_query("SELECT * FROM all_coxhrs WHERE prior = 'angina' AND outcome = 'heart failure' AND lag_hr IS NULL;", engine)
#             d = dict(zip(df.keys(),df.values[0]))
#             np.exp(-d['bch'] * np.exp(np.dot(
#                 lifelines.utils.normalize(np.array([datetime.datetime.today().year - 78, True, 0]),
#                                       np.array([d['year_norm_mean'],d['prior_norm_mean'],d['sex_norm_mean']]),
#                                       std=1),
#                 np.array([d['year_coef'], d['prior_coef'], d['sex_coef']])
#             )))
#             '''))

# gpt.add_example(
#     Example('I am a 78-year-old man with angina. What is my risk of having heart failure?',
#             '''
#             df=pd.read_sql_query("SELECT * FROM all_coxhrs WHERE prior = "angina" AND outcome = "heart failure" AND lag_hr IS NULL;", engine) \n   d=dict(zip(df.keys(),df.values[0])) \n   np.exp(-d["bch"]*np.exp(np.dot(lifelines.utils.normalize( np.array([datetime.datetime.today().year - 78, True, 0]),\n np.array([d["year_norm_mean"],d["prior_norm_mean"],d["sex_norm_mean"]]),\n std=1),\n np.array([d["year_coef"], d["prior_coef"], d["sex_coef"]])\n )))
#             '''
#             ))
# gpt.add_example(
#     Example('I am a guy at 40 with angina. What is my risk of having headache?',
#             '''
#             df=pd.read_sql_query("SELECT * FROM all_coxhrs WHERE prior = "angina" AND outcome = "headache" AND lag_hr IS NULL;", engine) \n   d=dict(zip(df.keys(),df.values[0])) \n   np.exp(-d["bch"]*np.exp(np.dot(lifelines.utils.normalize( np.array([datetime.datetime.today().year - 40, True, 0]),\n np.array([d["year_norm_mean"],d["prior_norm_mean"],d["sex_norm_mean"]]),\n std=1),\n np.array([d["year_coef"], d["prior_coef"], d["sex_coef"]])\n )))
#             '''
#             ))
# gpt.add_example(
#     Example('I am a 53-year-old woman with a history of stroke. What is my risk of having angina?',
#             '''
#             df=pd.read_sql_query("SELECT * FROM all_coxhrs WHERE prior = "stroke" AND outcome = "angina" AND lag_hr IS NULL;", engine) \n   d=dict(zip(df.keys(),df.values[0])) \n   np.exp(-d["bch"]*np.exp(np.dot(lifelines.utils.normalize( np.array([datetime.datetime.today().year - 53, True, 1]),\n np.array([d["year_norm_mean"],d["prior_norm_mean"],d["sex_norm_mean"]]),\n std=1),\n np.array([d["year_coef"], d["prior_coef"], d["sex_coef"]])\n )))
#             '''
#             ))
# gpt.add_example(
#     Example('What is my risk of angina if I am a female at 33 with a history of heart attack?',
#             '''
#             df=pd.read_sql_query("SELECT * FROM all_coxhrs WHERE prior = "heart attack" AND outcome = "angina" AND lag_hr IS NULL;", engine) \n   d=dict(zip(df.keys(),df.values[0])) \n   np.exp(-d["bch"]*np.exp(np.dot(lifelines.utils.normalize( np.array([datetime.datetime.today().year - 33, True, 1]),\n np.array([d["year_norm_mean"],d["prior_norm_mean"],d["sex_norm_mean"]]),\n std=1),\n np.array([d["year_coef"], d["prior_coef"], d["sex_coef"]])\n )))
#             '''
#             ))

gpt.add_example(
    Example('I am a 78-year-old man with angina. What is my risk of having heart failure?',
            'angina, heart failure, 78, male'))
gpt.add_example(
    Example('I am a 53-year-old woman with a history of stroke. What is my risk of having angina?',
            'stroke, angina, 53, female'))
gpt.add_example(
    Example('I am at 40 with angina. What is my risk of having headache?',
            'angina, headache, 40, na'))
gpt.add_example(
    Example('What is my risk of angina if I am a female with a history of heart attack?',
            'heart attack, angina, na, female'))
gpt.add_example(
    Example('I am a girl at 13 with migraine?',
            'migraine, na, 13, female'))
gpt.add_example(
    Example('If I have diabetes earlier, what is my risk of having hypertension?',
            'diabetes, hypertension, na, na'))
gpt.add_example(
    Example('if i have hypertension and i am 41, will I have stroke in the future?',
            'hypertension, stroke, 41, na'))


# I am a 65-year-old male. I had strke. What is my risk of epilepsy?
# I am a white American guy at 47 with migraine. What is my risk of stroke?
# I am a girl at 27 with lung cancer. I come from Japan. What is my risk of anemia?


# If I am a girl at 24 with lung cancer, what's my risk of having heart disease?
# I am a 65-year-old male. I had strke. What is my risk of epilepsy?

# age distrib
# {"hist": [["0—9", null], ["10—19", 0.0], ["20—29", 18.0], ["30—39", 53.0], ["40—49", 68.0], ["50—59", 83.0], ["60—69", 45.0], ["70—79", 22.0], ["80—89", 0.0], ["≥90", 0.0]]}

# gpt.add_example(
#     Example('I am a 53-year-old woman from Asia with a history of stroke. What is my risk of having angina?',
#             '''
#             create temporary table t as select P.*,H.icd10,H.date,D.diagnose_name from (
#             select distinct pt_id from Patient where (age between 50 and 55) and sex="F" and race="Asian") P
#             inner join (select pt_id,icd10,date from Hx) H on Patient.pt_id=Hx.pt_id
#             inner join Diagnose_code D on H.icd10=D.icd10;\n
#             select count(distinct t1.pt_id) as m from t t1 inner join (select * from t where diagnose_name="stroke") t2
#             on t1.pt_id=t2.pt_id and t1.date>t2.date where t1.diagnose_name="angina";\n
#             select count(distinct t1.pt_id) as n from t t1 inner join (select * from t where diagnose_name="stroke") t2
#             on t1.pt_id=t2.pt_id and t1.date>t2.date where t1.diagnose_name<>"angina";\n
#             m/(m+n);
#             '''))

# I am a white American guy at 47 with migraine. What is my risk of stroke?
# I am a girl at 27 with lung cancer. I come from Japan. What is my risk of anemia?
# I am a 65-year-old white American male. I had stroke. What is my risk of epilepsy?

# diag_df = pd.read_excel('ENDPOINT_ICD_FIN.xlsx', sheet_name='FINAL')
# diag_list = list(diag_df.LONGNAME)
with open('endpoint_list.json') as f:
    diag_list = json.load(f)
# diag_list = [i.lower() for i in diag_list]

def processAnswer(answer,match_part):
    '''
    match_part - 'disease_pre', 'disease_post'
    '''
    if match_part == 'prior = ':
        a = 'disease'
    else:
        a = 'risk'
    try:
        disease_pre = re.search(match_part+r'"([a-z][a-z\s]*)"', answer).group(1)
        disease = re.sub(r'(problem|disease)s{0,}( in){0,1}','',disease_pre).strip()
        disease_list = [diag for diag in diag_list if disease.lower().capitalize() in diag]
    except:
        print(answer)
        disease_list = []
    if len(disease_list) == 0:
        ratio = process.extract(disease.lower().capitalize(),diag_list)
        disease_list = [i[0] for i in ratio]
#     try:
#         disease_pre = re.search(r'disease_pre = "([a-z][a-z\s]*)"', answer).group(1)
#         disease_pre_list = [diag for diag in diag_list if disease_pre.upper() in diag]
#     except:
#         # cannot find anything
#         return 
    if len(disease_list) > 1:
        if match_part == 'outcome = ':
            q = 'Hey, what type of '+a+' do you have?'
        else:
            q = 'Hey, what type of '+a+' you are asking?'
#         return 'Hey, what type of '+disease_pre+' do you have?\n'+str(disease_list)
    elif len(disease_list) == 0:
        q = 'No disease in db matches the '+a+' you described, can you say it in another way?'
    else:
        if match_part == 'outcome = ':
            q = re.sub(r'prior = "([a-z][a-z\s]*)"',r'prior = "'+disease_list[0]+'"', answer)
        else:
            q = re.sub(r'outcome = "([a-z][a-z\s]*)"',r'outcome = "'+disease_list[0]+'"', answer)
    return q, disease_list

@app.route('/')

def root():

    return app.send_static_file('index.html')

@app.route("/translate", methods=["POST"])
def translate():
    def get_answer(prompt):
        response = gpt.submit_request(prompt)
        offset = 0
        if not gpt.append_output_prefix_to_query:
            offset = len(gpt.output_prefix)
        return response['choices'][0]['text'][offset:-len(gpt.output_suffix)]
    # pylint: disable=unused-variable
    prompt = request.json["prompt"]
    answer = get_answer(prompt)
    response = re.split('\n\s{5,}',answer)[1]
    text_pre, list_pre = processAnswer(response,'prior = ')
    text_post, list_post = processAnswer(response,'outcome = ')

    # return jsonify(answer: response,text_pre: text_pre,text_post: text_post,list_pre: list_pre,list_post:list_post)
    msg = {
        'answer': response,
        'text_pre': text_pre,
        'text_post': text_post,
        'list_pre': list_pre,
        'list_post': list_post
    }
    # print(msg['text_pre'])
    print(msg['answer'])
    return jsonify(message = msg)

# @app.route("/getDashboard", methods=["POST"])
# def get_data_for_dashboard():
#     parameters = request.get_json()
#     opt1 = str(parameters['opt1'])
#     opt2 = str(parameters['opt2'])
#     message = data_process.get_data(opt1, opt2)
#     return jsonify(message = message)


if __name__ == '__main__':

    # app.run(debug=True)
    app.run(debug=True,host='0.0.0.0', port=5000)


