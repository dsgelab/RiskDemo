import os
import openai
import pandas as pd
import numpy as np
import lifelines
import datetime, re
from fuzzywuzzy import process
from gpt import GPT, Example
from flask import Flask, request, jsonify
import json
import itertools
from sqlalchemy import create_engine

from sklearn.metrics.pairwise import cosine_similarity
import transformers
from sentence_transformers import SentenceTransformer, LoggingHandler



engine = create_engine('postgresql://gpt3')

global gpt

app = Flask(__name__, static_url_path='')
openai.api_key = os.getenv("OPENAI_API_KEY")

gpt = GPT(engine="curie",
          temperature=0,
          max_tokens=300)
# davinci curie babbage ada

gpt.add_example(
    Example('I am a 78-year-old man with angina. What is my risk of having heart failure?',
            'angina, heart failure, 78, male'))
gpt.add_example(
    Example('What is my risk of having angina if I am a 53-year-old woman with a history of stroke?',
            'stroke, angina, 53, female'))
gpt.add_example(
    Example('I am at 40 with angina. What is my risk of having headache?',
            'angina, headache, 40, na'))
gpt.add_example(
    Example('I am a guy at 47 with migraine. What is my risk of stroke?',
            'migraine, stroke, 47, male'))
gpt.add_example(
    Example('What is my risk of angina if I am a female with a history of heart attack?',
            'heart attack, angina, na, female'))
gpt.add_example(
    Example('I am a girl at 13 with migraine?',
            'migraine, na, 13, 1'))
gpt.add_example(
    Example('If I have diabetes earlier, what is my risk of having hypertension?',
            'diabetes, hypertension, na, na'))
gpt.add_example(
    Example('if i have hypertension and i am 41, will I have stroke in the future?',
            'hypertension, stroke, 41, na'))
gpt.add_example(
    Example('I am a girl at 27 with lung cancer. I come from Japan. What is my risk of anemia?',
            'lung cancer, anemia, 27, female'))
gpt.add_example(
    Example("What's the risk of having diabetes if I have fatty liver?",
            'fatty liver, diabetes, na, na'))

# I am a 65-year-old male. I had strke. What is my risk of epilepsy?
# I am a white American guy at 47 with migraine. What is my risk of stroke?
# I am a girl at 27 with lung cancer. I come from Japan. What is my risk of anemia?
# What is my risk of having heart failure if I had cardiovascular disease earlier? I am a woman at 65.
# Suppose I have cardiovascular disease and I am a man at 70. What's my risk of having heart failure problem?
# I am guy with strke. What is my risk of epilepsy?

# If I am a girl at 24 with lung cancer, what's my risk of having heart disease?
# I am a 65-year-old male. I had strke. What is my risk of epilepsy?

# I am a white American guy at 47 with migraine. What is my risk of stroke?
# I am a girl at 27 with lung cancer. I come from Japan. What is my risk of anemia?
# I am a 65-year-old white American male. I had stroke. What is my risk of epilepsy?


with open('/Users/feiwang/Documents/Data/endpoint_list.json') as f:
    endpoint_list = json.load(f)
endpoint_list = [(i[0], i[1]) for i in endpoint_list]
prior_list = set(list(zip(*endpoint_list))[0])
outcome_list = set(list(zip(*endpoint_list))[1])


def processAnswer(answer):
    """
    Input:
    answer pattern: list - 'disease_pre', 'disease_post', 'age', 'sex' (M: 0; F: 1)
    e.g. ['cancer', 'anemia', '27', '0']

    Output:
    question_index: dictionary -  pair: 1 - multi disease pairs are found; 2 - No disease pair is found
                                  age: 1 - no age
                                  sex: 1 - no gender
    question_dict: dictionary -  {pair:'', age:'', sex:''}
    choice_dict: dictionary -  {pre:'', post:''}
    modified_answer
    """
    # TODO: create a def for disease pre and post to avoid cohesion
    # TODO: what to do if no disease is found?
    # TODO: what if len of answer is not 4?

    question_dict = {'pair': 'Can you specify the disease you have and the risk you concern?',
                     'age': 'Can you tell me your age?',
                     'sex': 'Can you tell me your gender?'}
    choice_dict, question_index = {}, {}

    if answer[0] == 'na' or answer[1] == 'na':
        question_dict['pair'] = 'Sorry'
        question_index['pair'] = 2
        return answer, question_index, question_dict, choice_dict

    if answer[-1] == 'female':
        answer[-1] = '1'
    elif answer[-1] == 'male':
        answer[-1] = '0'

    try:

        disease_pre = re.sub(r'(problem|disease)s{0,}( in){0,1}', '', answer[0])
        disease_post = re.sub(r'(problem|disease)s{0,}( in){0,1}', '', answer[1])
        disease_list_pre = [diag for diag in prior_list if disease_pre.strip() in diag.lower()]
        disease_list_post = [diag for diag in outcome_list if disease_post.strip() in diag.lower()]
        disease_pair = list(itertools.product(disease_list_pre, disease_list_post))
        possible_disease_pair = [i for i in disease_pair if i in endpoint_list]
        print('disease_pre: ' + str(disease_pre))
        print('possible_disease_pair: ' + str(possible_disease_pair))
        print()

        if len(possible_disease_pair) == 0:
            ratio_pre = process.extract(disease_pre.lower().capitalize(), prior_list)
            disease_list_pre = [i[0] for i in ratio_pre]
            ratio_post = process.extract(disease_post.lower().capitalize(), outcome_list)
            disease_list_post = [i[0] for i in ratio_post]
            disease_pair = list(itertools.product(disease_list_pre, disease_list_post))
            possible_disease_pair = [i for i in disease_pair if i in endpoint_list]
            print('disease_list_post: ' + str(disease_list_post))
            print('possible_disease_pair: ' + str(possible_disease_pair))

        if len(possible_disease_pair) > 1:
            question_index['pair'] = 1
            choice_dict['pre'] = list(set(list(zip(*possible_disease_pair))[0]))
            choice_dict['post'] = list(set(list(zip(*possible_disease_pair))[1]))
        elif len(possible_disease_pair) == 0:
            question_dict[
                'pre'] = 'No disease in the database matches the one you have, can you describe it in another way?'
            question_index['pair'] = 2
            return answer, question_index, question_dict, choice_dict
        else:
            question_index['pair'] = 0
            answer[0], answer[1] = possible_disease_pair[0][0], possible_disease_pair[0][1]

        # if len(disease_list_post) == 0:
        #     ratio_post = process.extract(disease_post.lower().capitalize(),outcome_list)
        #     disease_list_post = [i[0] for i in ratio_post]
        # if len(disease_list_post) > 1:
        #     question_index['post'] = 1
        #     choice_dict['post'] = disease_list_post
        # elif len(disease_list_post) == 0:
        #     question_dict['post'] = 'No disease in the database matches the risk you concern, can you describe it in another way?'
        #     question_index['post'] = 2
        # else:
        #     question_index['post'] = 0
        #     answer[1] = disease_list_post[0]

        if answer[2] == 'na':
            question_index['age'] = 1
        if answer[3] == 'na':
            question_index['sex'] = 1

        if answer[0] == 'na':
            question_dict[
                'pre'] = 'No disease in the database matches the one you have, can you describe it in another way?'
            question_index['pre'] = 2
        if answer[1] == 'na':
            question_dict[
                'post'] = 'No disease in the database matches the risk you concern, can you describe it in another way?'
            question_index['post'] = 2

        answer = [possible_disease_pair[0][0], possible_disease_pair[0][1], answer[2], answer[3]]

    except Exception as e:
        print(e)
        print(answer)

    return answer, question_index, question_dict, choice_dict


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route("/translate", methods=["POST"])
def translate():
    # def get_answer(prompt):
    #     response = gpt.submit_request(prompt)
    #     offset = 0
    #     if not gpt.append_output_prefix_to_query:
    #         offset = len(gpt.output_prefix)
    #     return response['choices'][0]['text'][offset:-len(gpt.output_suffix)]
    # pylint: disable=unused-variable
    prompt = request.json["prompt"]
    answer = gpt.submit_request(prompt)['choices'][0]['text'].split(', ')
    print(answer)
    answer, question_index, question_dict, choice_dict = processAnswer(answer)

    msg = {
        'answer': answer,
        'question_index': question_index,
        'question_dict': question_dict,
        'choice_dict': choice_dict
    }
    print(msg['answer'])
    print(msg['question_index'])

    return jsonify(message=msg)


@app.route("/getRisk", methods=["POST"])
def getRisk():
    result = request.json["result"].split(',')
    prior = result[0].replace('&', ',')
    outcome = result[1].replace('&', ',')
    follow_up_years = request.json["years"]
    mean_indiv = pd.DataFrame({
        "BIRTH_TYEAR": [datetime.datetime.today().year - int(result[2])],
        "endpoint": [True],
        "female": [int(result[3])]
    })
    try:
        r = pd.read_sql_query(
            "SELECT * FROM cox_hrs as c, phenocodes as p_a, phenocodes as p_b WHERE p_a.id = c.prior_id AND p_b.id = c.outcome_id AND c.lagged_hr_cut_year = " + follow_up_years + " AND p_a.longname =  '" + prior + "' AND p_b.longname = '" + outcome + "';",
            engine).iloc[0, :]
        abs_risk = 1 - np.exp(- r.bch_year_21p99 * np.exp(np.dot(
            lifelines.utils.normalize(mean_indiv, mean=[r.year_norm_mean, r.prior_norm_mean, r.sex_norm_mean], std=1),
            [r.year_coef, r.prior_coef, r.sex_coef])))[0]
        return jsonify(
            message={"part1": "Your risk of having " + outcome + " is ", "part2": "{0:.2%}".format(abs_risk)})
    except IndexError as e1:
        print('Error type:' + str(e1))
        return jsonify(message={"part1": "No record is found with the input: \n", "part2": str(
            [prior, outcome, datetime.datetime.today().year - int(result[2]), result[3]])})


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
