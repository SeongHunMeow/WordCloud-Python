from wordcloud import WordCloud
from konlpy.tag import Twitter
from collections import Counter
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify
#CORS 처리.
from flask_cors import CORS
#파일에 접근하기 위한 라이브러리
import os

# 플라스크 웹 서버 객체 생성
app  = Flask(__name__, static_folder='outputs')
CORS(app)

#폰트 경로 설정
font_path = 'NanumGothic.ttf'

def get_tags(text, max_count, min_length):
    t = Twitter()
    nouns = t.nouns(text) #한글 명사만 추출
    processed = [n for n in nouns if len(n) >= min_length]
    count = Counter(processed) #각 명사의 출력 횟수
    result = {}
    # most_common 함수를 이용해서 max_count 갯수만큼만 뽑아냄
    for n, c in count.most_common(max_count):
        result[n] = c
    if len(result) == 0:
        result["내용이 없습니다."] = 1
    return result

def make_cloud_image(tags, file_name):
    #만들고자 하는 워드 클라우드의 기본 설정
    word_cloud = WordCloud(
        font_path=font_path,
        width=800,
        height=800,
        background_color="white"
    )
    #등장한 명사의 빈도 수를 이용해 워드클라우드 추출
    word_cloud = word_cloud.generate_from_frequencies(tags)
    #이미지 객체로 담는다.
    fig = plt.figure(figsize=(10, 10))
    plt.imshow(word_cloud)
    plt.axis("off")
    # 만들어진 이미지 객체를 파일 형태로 저장
    fig.savefig("outputs/{0}.png".format(file_name))


def process_from_text(text, max_count, min_length, words, file_name):
    tags = get_tags(text, int(max_count), int(min_length))
    #단어 가중치 적용
    for n, c in words.items():
        if n in tags:
            tags[n] = tags[n] * float(words[n])
    make_cloud_image(tags, file_name)

@app.route("/process", methods=['GET', 'POST'])
def process():
    content = request.json
    words = {}
    if content['words'] is not None:
        for data in content['words'].values():
            words[data['word']] = data['weight']
    process_from_text(content['text'], content['maxCount'], content['minLength'], words, content['textID'])
    result = {'reuslt': True}
    return jsonify(words)

@app.route('/outputs', methods=['GET', 'POST'])
def output():
    text_id = request.args.get('textID')
    return app.send_static_file(text_id + '.png')

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    text_id = request.args.get('textId')
    path = "outputs/{0}.png".format(text_id)
    result = {}
    # 이미지 파일 존재 여부 확인
    if os.path.isfile(path):
        result['result'] = True
    else:
        result['result'] = False
    return jsonify(result)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, threaded=True)