import pandas
import random
import re
from io import StringIO
import requests

class InputHandler:
    templates = ['bvnw_3_;znw_2_ev;<\n>bvnw_2_;znw_3_mv;ww_2_mv;<\n>znw_5_ev',
                 "bvnw_3_;znw_2_;<\n>bvnw_2;znw_3_;ww_2_;<\n>telwoord_1_;bvnw_2;znw_2_mv",
                 "bezvnw_1_;znw_2_ev;<en>persvnw_1_;<\ntijdens de>znw_3_ev;ww_1_ev;persvnw_1;<\neen>quantifier_2_;znw_2_",
                 "<een>quantifier_1_;znw_3_mv;<\n>vz_1_;<de>znw_1_ev;<waar>bwb_3_;telwoord_1_mv;<\n>znw_2_mv;ww_2_mv",
                 "vz_1_;<een>bvnw_2_;znw_1_ev;<\n>ww_1_ev;<een>bvnw_3_;znw_1_;bwb_1_;<\nte>ww_3_mv",
                 "<nu>persvnw_1_ev;bvnw_1_;ww_1_ev;<toch\n maar even>ww_3_mv;<\ntot het>bvnw_2_;ww_1_ev"]
    woordenlijst_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTGcnOl_KxaYZhQhv8hzb7Ho28NUh8p0BjdSA0cvqO2brdqzbmICLg406okO7je2TaT0qiQevCyPMoM/pub?gid=908729767&single=true&output=csv"

    def __init__(self, input_word_list):
        self.input_word_list = input_word_list
        self.word_df = self._retrieve_word_list()
        self.injected_templates = self._search_n_inject_templates()

    def pick_injected_template(self):
        if len(self.injected_templates) > 0:
            rand_int = random.randint(0, len(self.injected_templates) - 1)
            return self.injected_templates[rand_int]
        else:
            rand_int = random.randint(0, len(self.templates))
            return self.templates[rand_int]

    def _search_n_inject_templates(self):
        # TODO: perform random word choice in other function for transparency
        word_descriptions_dict_collection = self._match_input_with_worddf()
        randindex = random.randint(0, len(word_descriptions_dict_collection) - 1)
        random_word_description_dict = word_descriptions_dict_collection[randindex]
        first_matched_word_dict = random_word_description_dict['retrieved_word']
        self.category_dict = random_word_description_dict['category_dict']
        injected_templates = self._inject_word_in_templates(first_matched_word_dict)
        return injected_templates

    def _retrieve_word_list(self):
        woordenlijst_text = requests.get(self.woordenlijst_url).text
        woordenlijst = pandas.read_csv(StringIO(woordenlijst_text))
        return woordenlijst

    def _match_input_with_worddf(self):
        retrieved_word_list = []
        for word in self.input_word_list:
            retrieved_word = self.word_df[self.word_df.iloc[:, 0] == word]
            if not retrieved_word.empty:
                potential_seasons = retrieved_word['seizoen'].values[0]
                season = self._enforce_single_season(potential_seasons)
                retrieved_word_list += [{"retrieved_word": retrieved_word,
                        "category_dict": {"season": season}}]
        if len(retrieved_word_list) > 0:
            return retrieved_word_list
        else:
            return self._make_up_retrieved_word_description()

    def _make_up_retrieved_word_description(self):
        # TODO: makeup something better than a random word
        proverb_df = self.word_df[self.word_df['woordsoort'] == 'znw']
        randindex = random.randint(0, len(proverb_df) - 1)
        random_word = proverb_df.iloc[randindex:randindex+1]
        potential_seasons = random_word['seizoen'].values[0]
        season = self._enforce_single_season(potential_seasons)
        return [{"retrieved_word": random_word,
                        "category_dict": {"season": season}}]

    def _inject_word_in_templates(self, retrieved_word_dict):
        template_code_word = self._get_template_code_of_word(retrieved_word_dict).replace('ev', '')
        word = retrieved_word_dict['Woord'].values[0]
        injected_template_list = []
        for template in self.templates:
            template_codes = template.split(';')
            for index, template_code in enumerate(template_codes):
                if template_code.endswith(template_code_word):
                    replacement = self._replace_template_code_with_word(template, index, word, template_code_word)
                    injected_template_list += [replacement]
        return injected_template_list

    def _get_template_code_of_word(self, word):
        woordsoort = word['woordsoort'].values[0]
        lettergrepen = str(int(word['aantallettergrepen'].values[0]))
        ev_of_mv = word['ev of mv'].values[0]
        template_code = "_".join([woordsoort, lettergrepen, ev_of_mv])
        return template_code

    def _replace_template_code_with_word(self, template, index, word, template_code):
        template_codes = template.split(';')
        template_codes[index] = template_codes[index].replace(template_code, "<" + word + ">")
        if '><' in template_codes[index]:
            template_codes[index] = template_codes[index].replace('><', '')
        return ";".join(template_codes)

    @staticmethod
    def _enforce_single_season(potential_seasons):
        potential_seasons_list = potential_seasons.split('/')
        random_season_index = random.randint(0, len(potential_seasons_list) - 1)
        picked_season = potential_seasons_list[random_season_index]
        return picked_season




class HaikuTextGenerator:
    template_word_pattern = '<(.*?[\r?\n]?.*?)>'

    def __init__(self, worddf, template, category_dict):
        self.template = template
        self.word_dataframe = worddf
        self.debug = False
        self.category_dict = category_dict
        self._parse_template()

# Public methods
    def compose_haiku(self):
        words = self._perform_search()
        haiku = ""
        for index, word in enumerate(words):
            if index in self._template_words_dict:
                word_to_inject = self._template_words_dict[index]
                if word_to_inject:
                    haiku += ' ' + word_to_inject
            haiku += ' ' + word
        haiku = haiku.replace('\n', ',')
        return haiku

# Private methods
    def _parse_template(self):
        self._encodings = self.template.split(";")
        self._extract_predefined_template_words()
        filter_criteria_list = [word.split("_") for word in self._encodings]
        self._filter_criteria_list = self._inject_category_filter(filter_criteria_list)

    def _inject_category_filter(self, filter_criteria_list):
        key = next(iter(self.category_dict))
        for filter_criteria in filter_criteria_list:
            filter_criteria += [self.category_dict[key]]
        return filter_criteria_list

    def _extract_predefined_template_words(self):
        self._template_words_dict = {index: self._return_pattern_match(encoding) for
                                     index, encoding in enumerate(self._encodings)}
        self._remove_template_words()

    def _return_pattern_match(self, encoding):
        match = re.search(self.template_word_pattern, encoding)
        if match:
            return match.group(1)
        else:
            return ''

    def _remove_template_words(self):
        for index, encoding in enumerate(self._encodings):
            self._encodings[index] = re.sub(self.template_word_pattern, '', encoding)

    def _perform_search(self):
        words = [self._pick_word_from_word_df(self._filter_worddf_complete(filter_criteria)) for
                 filter_criteria in self._filter_criteria_list]
        return words

    def _filter_column_worddf(self, filtered_worddf, filter_criterium, column_index):
        if not filter_criterium:
            return filtered_worddf
        else:
            filtered_rows = filtered_worddf.iloc[:, column_index].astype(str)\
                .str.replace('.0', '')\
                .str.contains(filter_criterium)
            if not filtered_rows.sum():
                if self.debug:
                    print('filter_criteria failed: `{0}` for column {1}, '
                      'picking empty filter criterium'.format(filter_criterium, column_index))
                return filtered_worddf
            return filtered_worddf[filtered_rows]

    def _filter_worddf_complete(self, filter_criteria):
        filtered_worddf = self.word_dataframe.copy(True)
        for index, filter_criterium in enumerate(filter_criteria):
            filtered_worddf = self._filter_column_worddf(filtered_worddf, filter_criterium, index + 1)
        return filtered_worddf.iloc[:,0].tolist()

    @staticmethod
    def _pick_word_from_word_df(words):
        random_index = random.randint(0, len(words) - 1)
        return words[random_index]
