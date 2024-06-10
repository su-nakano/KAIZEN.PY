from datetime import datetime
import json
import os
import re

from bs4 import BeautifulSoup

def scrape_question_texts(page_source, icon_number, url, iterateNum):
    print("icon_number, ==========================%d=====================================", icon_number)
    soup = BeautifulSoup(page_source, 'html.parser')

    category_text = soup.find('li', class_=f'icon-0{icon_number} active').text
    category_title = f'{category_text}に関する質問'

    faq_section = soup.find('section', class_='fq-list-box js-tabContents is-show')
    # 質問のタイトルの場所を確認
    question_titles = faq_section.find('dl', class_='faqlist__item js-faqAccordion')

    # 'lazyload' か 'lazyloaded' がクラス名になっている質問Elementを抽出
    faq_elements = []
    question_titles = faq_section.find('dl', class_='faqlist__item js-faqAccordion')
    if len(question_titles.find_all('dt', class_='lazyloaded')) > 0:
        for element in question_titles.find_all('dt', class_='lazyloaded'):
            faq_elements.append(element)

    if len(question_titles.find_all('dt', class_='lazyload')) > 0:
        for element in question_titles.find_all('dt', class_='lazyload'):
            faq_elements.append(element)

    # dtタグで囲まれている質問のテキストのみを抽出
    faq_texts = [faq.text.strip() for faq in faq_elements]
    # 質問文へのLinkを抽出
    faq_text_links = [ f'{url}#{i + 1}' for i in range(0,len(faq_elements))]

    return category_title, faq_texts, faq_text_links

def scrape_answer_texts(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    faq_section = soup.find('section', class_='fq-list-box js-tabContents is-show')
    # QA要素がある場所を確認して、回答のみ抽出
    question_titles = faq_section.find('dl', class_='faqlist__item js-faqAccordion')
    answers =  question_titles.find_all('dd')

    # 文字だけを抽出
    answer_texts = [process_text(answer.text.strip()) for answer in answers]

    return answer_texts


def convert_texts_into_q_with_links_list(categoryTitle, questionTexts, links, answerTexts, iterateNum):
    # 出力用の構造体を作成
    output = {
        "categoryId": f'{100000 + iterateNum + 1}',
        "category": categoryTitle,
        "questions": [],
        "answers": []
    }

    # 質問と回答をリストに追加
    for i, (question, answer, link) in enumerate(zip(questionTexts, answerTexts, links)):
        question_id = f"Q{(iterateNum+1) * 10000 + i}"
        keywords_question = question.split()
        keywords_answer = answer.split()

        output["questions"].append({
            "id": question_id,
            "title": question,
            "index": keywords_question
        })
        
        output["answers"].append({
            "questionId": question_id,
            "content": answer,
            "link": link,
            "index": keywords_answer
        })
    
    return output

def convert_category_title_to_group(categoryTitle, iterateNum):
    return {
        "id": f'{100000 + iterateNum + 1}',
        "title": categoryTitle,
        "index": categoryTitle.split()
    }
    

def push_obj_to_list(list, obj):
    list.append(obj)
    return list

def push_qa_category_to_first_question_list(firstQuestionList, categoryTitles):

    for(categoryTitle,i) in categoryTitles:
       categoryObj =  {
           'id': f'{100000 + i + 1}',
           'title': categoryTitle,
           'index': categoryTitle.split()
       }
    firstQuestionList.append(categoryObj)
    return firstQuestionList

def create_dir(base_dir):
    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
    # 現在の日付と時刻を使用して新しいディレクトリを作成
    dir_path = os.path.join(base_dir, current_datetime)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def export_to_json(qaList, file_path, file_name):
    """Export the qaList object to a JSON file."""
    # JSONファイルのパスを定義
    dir_path = create_dir(file_path)
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(qaList, json_file, ensure_ascii=False, indent=4)


def process_text(text):
    # 改行を<br>に変換
    text = text.replace('\n', '<br>')
    # 複数の<br>を1つにまとめる
    text = re.sub(r'(?:<br>)+', '<br>', text)
    # タブ補完を削除
    text = text.replace('                 ', '')
    # URLを<a>タグに変換
    url_pattern = re.compile(r'(https://[^\s]+)')
    text = url_pattern.sub(r'<a href="\1" target="_blank">\1</a>', text)
    
    # aタグに含まれる<br>を削除
    text = re.sub(r'<a href="([^"]*?)<br>([^"]*?)"', r'<a href="\1\2"', text)
    text = re.sub(r'(\bhttps://[^\s]+)<br>(</a>)', r'\1\2', text)

    return text
