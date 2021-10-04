# Autor: Andreas Wagner
# Datum: 10.09.2021
# Institution: Friedrich-Alexander-Universität Erlagnen-Nürnberg
# Bachelorarbeit
# Betreuer: Dr. Dominik Kremer
# Titel: Regionale Bezogenheit des Klimabegriffs im Zeitwandel in verschiedenen regionalen Printmedien
# ___________________________________________
# installation of packages with 'pip install' via the terminal
#   -nltk (Version 3.6.2)
#   -pandas (Version 1.2.4)
#   -geopy (Version 2.2.0)
#   -HanTa (Version 0.2.0)
# download of the german Stanford-Tagger (from https://nlp.stanford.edu/software/tagger.shtml)
# ____________________________________________
# imports:
import os
import json
import nltk
from datetime import datetime
import pandas as pd
from HanTa import HanoverTagger as ht
from nltk.tag import StanfordNERTagger
from geopy import Nominatim
import operator


# ________________________________
# set the os-Environment for NER Tagging
os.environ['JAVAHOME'] = "C:/Program Files (x86)/Java/jre1.8.0_301/bin/java.exe"
# _________________________________
# base-function for saving data as json


def write_json(data, filename):
    with open(filename + '.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
# _______________________________
# functions for inspecting the data


def print_corpora(name):
    df = pd.read_json("./Daten/" + name + ".json")
    for elem in df.articles:
        print(elem['citation'])
        print(elem['text'])
        print('_______________________________________________________')
# _______________________________
# create the jsons from the .txt files

# to run this on a corpus from COSMASII the .txt file must be adapted:
#   - the empty lines between the underscore after the head information an the first text-data must be removed
#   - a line (in the same length as after the head) must be inserted before the footer


def segregate_data(rel_path, name):
    f_path = rel_path + name
    f = open(f_path, "r")
    data = f.read()
    # seperate the head and foot of the document
    seperate_head = data.split("________________________________________________________________________________")
    head = seperate_head[0]+seperate_head[1]
    stats = seperate_head[3]
    body = seperate_head[2].split("\n\n")
    # write data into json file
    corp_json = {
        'name': name,
        'metadata': head,
        'statistic': stats,
        'articles': []}
    # seperate citation from text
    for i in range(len(body)):
        if i % 2 == 1:
            text_stripped = body[i].replace("<B>", "")
            text_stripped = text_stripped.replace("</>", "")
            text_dict = {
                'citation': body[i - 1],
                'text': text_stripped
            }
            corp_json['articles'].append(text_dict)
    datei = os.path.splitext(name)[0]
    with open("./Daten/" + datei + '.json', 'w') as outfile:
        json.dump(corp_json, outfile)
    f.close()
# ______________________________
# analysis functions


def count_sentences(corpus, name):
    sentence_list = []
    word_count = []
    for article_number in range(len(corpus)):
        # the article variable contains a dictionairy with 'citation' and 'text' keys
        article = corpus.articles[article_number]
        # print(article['citation'])
        # tokenisation sentences
        sentences = nltk.sent_tokenize(article['text'], language='german')
        for sentence in sentences:
            sentence_list.append(sentence)
            words = nltk.word_tokenize(sentence, language='german')
            for word in words:
                word_count.append(word)

    print(name, ": ", len(corpus.articles), " Artikel; ", len(sentence_list), " Sätze; ", len(word_count), " Wörter")
    return(len(corpus.articles), len(sentence_list), len(word_count))


def count_dict_elem(dict, total):
    new_dic = {}
    counter = 0
    for elem in dict.keys():
        year_dict = {}
        for year in dict[elem].keys():
            year_dict[year] = [len(dict[elem][year]), ((len(dict[elem][year])/total[counter])*100)]

        year_dict['total'] = [total[counter], 100]
        new_dic[elem] = year_dict
        counter += 1
    return(new_dic)



def count_per_year(corpus, name, count_total):
    art_dic = {'2017': [],
                    '2018': [],
                    '2019': [],
                    '2020': []}
    sentence_dic = {'2017': [],
                    '2018': [],
                    '2019': [],
                    '2020': []}
    word_dic = {'2017': [],
                    '2018': [],
                    '2019': [],
                    '2020': []}
    for article_number in range(len(corpus)):
        # the article variable contains a dictionairy with 'citation' and 'text' keys
        article = corpus.articles[article_number]
        citation = corpus.articles[article_number]['citation']
        date = citation.split(", ")[1]
        year = date.split(".")[2]
        art_dic[year].append(article)
        # print(article['citation'])
        # tokenisation sentences
        sentences = nltk.sent_tokenize(article['text'], language='german')
        for sentence in sentences:
            sentence_dic[year].append(sentence)

            words = nltk.word_tokenize(sentence, language='german')
            for word in words:
                word_dic[year].append(word)
    # print(name)
    # for elem in sentence_dic.keys():
    #     print(elem)
    #     print("Sentences: ", len(sentence_dic[elem]), "; ", ((len(sentence_dic[elem])/count_total[0])*100), "%" )
    #     print("Words: ", len(word_dic[elem]), "; ", ((len(word_dic[elem])/count_total[1])*100), "%")
    # print()

    dict_complete = {'articles': art_dic,
                    'sentences': sentence_dic,
                    'words': word_dic}

    count_complete = count_dict_elem(dict_complete, count_total)
    print(count_complete)
    com_df = pd.DataFrame.from_dict({(i,j): count_complete[i][j]
                           for i in count_complete.keys()
                           for j in count_complete[i].keys()},
                       orient='index', columns= ['Number','Percentage'])

    print(com_df)

    # sentence_dict_count = count_dict_elem(sentence_dic, count_total[0])
    # sent_df = pd.DataFrame.from_dict(sentence_dict_count, orient='index', columns=["Numbers","Percentages"])
    # print(sent_df)
    # word_dict_count = count_dict_elem(word_dic, count_total[1])
    # word_df = pd.DataFrame.from_dict(word_dict_count, orient='index', columns=["Numbers", "Percentages"])
    # print(word_df)


def pos_tagging(wordlist):
    tagger = ht.HanoverTagger('morphmodel_ger.pgz')
    tags = tagger.tag_sent(wordlist, taglevel=1)
    return(tags)


def create_bag_of_nouns(taglist):
    nounlist = []
    for word in taglist:
        if word[2] == 'NN' or word[2] == 'NE':
            nounlist.append(word[1])
        else:
            continue
    return(nounlist)


def get_location(tokenized_sentence):
    st = StanfordNERTagger('./NER/german-ner/edu/stanford/nlp/models/ner/german.distsim.crf.ser.gz',
                           './NER/stanford-ner-2020-11-17/stanford-ner.jar',
                           encoding='utf-8')
    tag = st.tag(tokenized_sentence)
    # check if the NER tag is a lcation
    loc_word = []
    for word in tag:
        if word[1] == 'LOCATION':
            loc_word.append(word[0])
        else:
            continue
    return(loc_word)


def bag_of_noun_dict(dic, words):
    for nouns in words:
        for noun in nouns:
            # insert a count mechanism
            if noun not in dic.keys():
                dic[noun] = 1
            else:
                dic[noun] += 1


# function for writing a dict for each location and append the count number, when location is there
def write_loc_dict(parent_list, location, sentence, citation, tagged):
    if len(parent_list) != 0:
        bool_location = (False, 0)
        for found_location_number in range(len(parent_list)):
            #print(found_location_number)
            found_location = parent_list[found_location_number]
            if found_location['location'] == location:
                print('found')
                bool_location = (True, found_location_number)
                break
            else:
                bool_location = (False, found_location_number)
            #print(bool_location)

        bool_sentence = False
        if bool_location[0]:
            for found_sentence in parent_list[bool_location[1]]['sentence']:
                if found_sentence == sentence:
                    bool_sentence = True
                    print(found_sentence, sentence)
                    print(bool_sentence)
                    break
                else:
                    bool_sentence = False

            if bool_sentence:
                print('sentence is there')
            else:
                parent_list[bool_location[1]]['count'] += 1
                parent_list[bool_location[1]]['sentence'].append(sentence)
                parent_list[bool_location[1]]['citation'].append(citation)
                parent_list[bool_location[1]]['tagged_sentence'].append(tagged)
                print('appended')
        else:
            locator = Nominatim(user_agent='andiw')
            loca = locator.geocode(location)
            if loca is None:
                print("It's not a Location")
            else:
                dict = {
                    "location": location,
                    "count": 1,
                    "sentence": [sentence],
                    "citation": [citation],
                    "tagged_sentence": [tagged]
                }
                parent_list.append(dict)
    # if the list is empty
    else:
        locator = Nominatim(user_agent='andiw')
        loca = locator.geocode(location)
        if loca == None:
            print("It's not a Location")
        else:
            dict = {
                "location": location,
                "count": 1,
                "sentence": [sentence],
                "citation": [citation],
                "tagged_sentence": [tagged]
            }
            parent_list.append(dict)
# _______________________


def nlp_pipeline(corpus, name):
    location_list_close = []
    location_list_wide = []
    wordfreq_0 = {}
    wordfreq_1 = {}
    for article_number in range(len(corpus)):
        print()
        print("Number: ", article_number, " from: ", len(corpus.articles))
        # the article variable contains a dictionairy with 'citation' and 'text' keys
        article = corpus.articles[article_number]
        #print(article['citation'])
        # tokenisation sentences
        sentences = nltk.sent_tokenize(article['text'], language='german')
        # variables for bag of words
        bag_of_words_close = []
        bag_of_words_wide = []
        for sentence_word_list in sentences:
            # tokenisation of words
            word_list = nltk.word_tokenize(sentence_word_list, language='german')
            # POS-Tagging
            tagged = pos_tagging(word_list)
            # seperate sentence with Keyword from the others
            if "Klimakrise" in sentence_word_list:
                # close bag of words
                bag_of_words_close.append(create_bag_of_nouns(tagged))
                # NER tagging and location extraction
                for location_close in get_location(word_list):
                    write_loc_dict(location_list_close,
                                   location_close,
                                   sentence_word_list,
                                   article['citation'],
                                   tagged)
            else:
                bag_of_words_wide.append(create_bag_of_nouns(tagged))
                for location_wide in get_location(word_list):
                    write_loc_dict(location_list_wide,
                                   location_wide,
                                   sentence_word_list,
                                   article['citation'],
                                   tagged)
        for elem in range(len(location_list_wide)):
            print(location_list_wide[elem]['location'], location_list_wide[elem]['count'])
            print(location_list_wide[elem]['sentence'])


        bag_of_noun_dict(wordfreq_0, bag_of_words_close)
        bag_of_noun_dict(wordfreq_1, bag_of_words_wide)
    complete_dict = {
        "context": [{
            "sentence_number": 0,
            "sentences": location_list_close
        }, {
            "sentence_number": 1,
            "sentences": location_list_wide
        }
        ]}
    #saving all the data to external files
    filename = "./Ergebnisse/"+name+"_tagged_loc"
    write_json(complete_dict, filename)
    bag_of_noun_names = "./Ergebnisse/"+name+"_BON_close_complete"
    write_json(wordfreq_0, bag_of_noun_names)
    sorted_d = sorted(wordfreq_0.items(), key=operator.itemgetter(1))
    # sort dict to get the 30 most used nouns
    close_frequ_sort = sorted_d[-31:-1]
    bag_of_noun_srtd = "./Ergebnisse/" + name + "_BON_close"
    # save the wide context bag of nouns
    write_json(close_frequ_sort, bag_of_noun_srtd)
    bag_of_noun_names_2 = "./Ergebnisse/"+name+"_BON_wide_complete"
    write_json(wordfreq_1, bag_of_noun_names_2)
    sorted_d2 = sorted(wordfreq_1.items(), key=operator.itemgetter(1))
    bag_of_noun_srtd_2 = "./Ergebnisse/" + name + "_BON_wide"
    wide_frequ_sort = sorted_d2[-30:]
    write_json(wide_frequ_sort, bag_of_noun_srtd_2)
    print('done')
    # no return values, because it's already saved into seperate files
# _______________________
# analyse the nlp-tagged elements


def create_precision(tagged_corpus, name):
    sentence_per_loc = []
    loc_per_sentence_number = []
    sentence_number = []
    precision = []
    citations = []
    date = []
    for all_sentences in tagged_corpus['context']:
        for numb in range(len(all_sentences['sentences'])):
            for n in range(len(all_sentences['sentences'][numb]['sentence'])):
                citations.append(all_sentences['sentences'][numb]['citation'][n].split(" ")[0])
                date.append(all_sentences['sentences'][numb]['citation'][n].split(", ")[1])
                sentence_per_loc.append(all_sentences['sentences'][numb]['sentence'][n])
                loc_per_sentence_number.append(all_sentences['sentences'][numb]['location'])
                sentence_number.append(all_sentences['sentence_number'])
                print(all_sentences['sentences'][numb]['location'])
                print(all_sentences['sentences'][numb]['sentence'][n])
                inp = input("implizit = 2; explizit = 1 ; irrelevant = 0")
                #inp = '1'
                if inp == '1':
                    precision.append(1)
                elif inp == '2':
                    precision.append(2)
                else:
                    precision.append(0)

                #print(precision)
    data_for_presicion = {'location':loc_per_sentence_number, 'sentence': sentence_per_loc, 'precision': precision,
                          'sentence_number':sentence_number, 'reference': citations, 'date': date}
    df_prec = pd.DataFrame.from_dict(data=data_for_presicion)
    df_prec.to_excel(r'./Ergebnisse/V1_'+name+'_Relevanz_precision.xlsx', sheet_name = 'Relevanz')
    df_prec.to_json('./Ergebnisse/V1_' + name + '_Relevanz_precision.json')


def create_time_line(tagged_courpus):
    for all_sentences in tagged_courpus['context']:
        if all_sentences['sentence_number'] == 0:
            df = pd.DataFrame.from_dict(all_sentences['sentences'])
            date_for_loc = []
            for nrb in range(len(df.location)):
                cit = df.citation[nrb]
                land = df.location[nrb]

                for el in cit:
                    splt = el.split(", ")
                    time = datetime.strptime(splt[1], '%d.%m.%Y').date()
                    raw_time = splt[1]
                    ref = splt[0].split(" ")[0]
                    my_tuple = (time, raw_time, land, ref)
                    date_for_loc.append(my_tuple)
            dataframe_year = []
            dataframe_month = []
            dataframe_day = []
            dataframe_raw_time = []
            dataframe_loc = []
            dataframe_ref = []

            for elem in date_for_loc:
                dataframe_year.append(elem[0].year)
                dataframe_month.append(elem[0].month)
                dataframe_day.append(elem[0].day)
                dataframe_raw_time.append(elem[1])
                dataframe_loc.append(elem[2])
                dataframe_ref.append(elem[3])

            data_per_year = {'date': dataframe_raw_time, 'year': dataframe_year, 'month': dataframe_month,
                             'day': dataframe_day,
                             'location': dataframe_loc, 'reference': dataframe_ref}
            df_orte = pd.DataFrame(data=data_per_year)
            sorted = df_orte.sort_values(['year', 'month', 'day'])
            print(sorted)


def count_unique_sentences(tagged_corpus, name):
    sentences = {}
    boolean = True
    for all_sentences in tagged_corpus['context']:
        sentence_list = []
        for numb in range(len(all_sentences['sentences'])):
            for n in range(len(all_sentences['sentences'][numb]['sentence'])):
                for ele in range(len(sentence_list)):
                    if all_sentences['sentences'][numb]['sentence'][n] == sentence_list[ele]:
                        boolean = False
                        break
                    else:
                        boolean = True

                if boolean:
                    sentence_list.append(all_sentences['sentences'][numb]['sentence'][n])

        sentences[all_sentences['sentence_number']] = sentence_list
    print(name)
    for k in sentences.keys():
        if k == 0:
            print('close')
            print(len(sentences[k]))
        else:
            print('wide')
            print(len(sentences[k]))


def count_articles(tagged_corpus, name):
    sentences = {}
    boolean = True
    for all_sentences in tagged_corpus['context']:
        art_list = []
        for numb in range(len(all_sentences['sentences'])):
            for n in range(len(all_sentences['sentences'][numb]['citation'])):
                for ele in range(len(art_list)):
                    if all_sentences['sentences'][numb]['citation'][n] == art_list[ele]:
                        boolean = False
                        break
                    else:
                        boolean = True


                if boolean:

                    art_list.append(all_sentences['sentences'][numb]['citation'][n])

        sentences[all_sentences['sentence_number']] = art_list
    print(name)
    for k in sentences.keys():
        if k == 0:
            print('close')
            print(len(sentences[k]))
        else:
            print('wide')
            print(len(sentences[k]))
# ______________________
# sequences


def preprocessing(name):
    # writing the data from the directionairy 'Rohdaten' into a seperate json
    segregate_data("Rohdaten/", name + ".TXT")


def analysis(name):
    #corpus = pd.read_json("./Daten/" + name + ".json")
    #nlp_pipeline(corpus, name)
    #total = count_sentences(corpus, name)
    #count_per_year(corpus, name, total)
    tagged_corpus = pd.read_json("./Ergebnisse/"+name+"_tagged_loc.json")
    #create_precision(tagged_corpus, name)
    #create_time_line(tagged_corpus)
    #count_unique_sentences(tagged_corpus, name)
    #count_articles(tagged_corpus, name)


def main():
    global_names = ["Ostseezeitung_2016_2020_Klimakrise", "NN_2017_2020_Klimakrise"]
    for name in global_names:
        #preprocessing(name)
        analysis(name)


if __name__ == "__main__":
    main()
