# -*- coding: utf-8 -*-
import re
import os
import pickle
from pathlib import Path
import urllib.request
from janome.charfilter import *
from janome.analyzer import Analyzer
from janome.tokenizer import Tokenizer
from janome.tokenfilter import *
from gensim import corpora
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
from utils import setup_folder

class ImageCreator:

    def extract_text(self, data_dir):
        """
        Extract text data from issue data

        Parameters
        ----------
        data_dir : String
            Directory which have issue data
        """
        assert data_dir.exists() and data_dir.is_dir(), "Data folder should exist."

        datafile = data_dir.joinpath("issues.pickle")
        print("read issues: %s" % datafile)
        if not datafile.exists():
            return
        # Load issue data
        with open(datafile, "rb") as f:
            issues = pickle.load(f)

        # Parse the issue data
        text = ""
        counter_notes = 0
        counter_comments = 0
        for issue in issues:
            text += issue.subject + "\n"
            text += issue.description + "\n"
            for journal in issue.journals:
                if hasattr(journal, "notes"):
                    # print(journal.notes))
                    text += journal.notes + "\n"
                    counter_notes += 1
            for changeset in issue.changesets:
                text += changeset["comments"] + "\n"
                counter_comments += 1
        print("total issues: %d, notes: %d, comments: %d" % (len(issues), counter_notes, counter_comments))

        # Export the text file (for debug)
        textfile = data_dir.joinpath("text.txt")
        print("write text: %s" % textfile)
        with open(textfile, 'w', encoding='utf-8') as f:
            f.write(text)
        return text

    def cleanup_text(self, text):
        """
        Remove unnecessary text from the input text

        Parameters
        ----------
        text : String
            Text to remove some words
        """
        # Remove URL
        text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', ' ', text)
        # Remove email address
        text = re.sub(r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', ' ', text)
        # Remove symbols
        text = re.sub(r'[!-/:-@[-`{-~]', ' ', text)
        text = re.sub(r'[■-♯①-⑨]', ' ', text)
        return text

    def parse_text_data(self, data_dir, text):
        """
        Parse text data for one project

        Parameters
        ----------
        data_dir : String
            Directory which have issue data
        text : String
            Text data to parse
        """
        assert data_dir.exists() and data_dir.is_dir(), "Data folder should exist."

        if (not text) or (len(text) == 0):
            print("Skip empty data")
            return

        # Filter to replace all numeric chars to '0'.
        class NumericReplaceFilter(TokenFilter):
            def apply(self, tokens):
                for token in tokens:
                    parts = token.part_of_speech.split(',')
                    if (parts[0] == '名詞' and parts[1] == '数'):
                        token.surface = '0'
                        token.base_form = '0'
                        token.reading = 'ゼロ'
                        token.phonetic = 'ゼロ'
                    yield token

        # Filter to remove single character.
        class OneCharacterReplaceFilter(TokenFilter):
            def apply(self, tokens):
                for token in tokens:
                    if re.match('^[あ-んア-ンa-zA-Z0-9ー]$', token.surface):
                        continue
                    yield token


        # Create the Tokenizer.
        tokenizer = Tokenizer()

        # Charater filter for Janome.
        char_filters = [ UnicodeNormalizeCharFilter() ]

        # Set up the filters
        token_filters = [
                        # NumericReplaceFilter(),
                        CompoundNounFilter(),
                        POSKeepFilter(['名詞', '動詞', '形容詞', '副詞']),
                        # OneCharacterReplaceFilter()
                        ]

        analyzer = Analyzer(char_filters, tokenizer, token_filters)

        token_list = []
        for line in text.splitlines():
            line = self.cleanup_text( line )
            # Parse the sentence and get the words.
            ss = [token.base_form for token in analyzer.analyze(line)]
            if len(ss) > 0:
                token_list.append(ss)

        # Create the word list
        words = []
        for line in token_list:
            words.extend([word+' ' for word in line if word != ''])

        # Export the words file (for debug)
        wordsfile = data_dir.joinpath("words.txt")
        print("total words: %d, write words: %s" % (len(words), wordsfile))
        with open(wordsfile, 'w', encoding='utf-8') as f:
            f.writelines(words)

        wlist = defaultdict(lambda: 0)
        for word in words:
            wlist[word] += 1
        print("total unique words: %d" % (len(wlist.keys())))

        wlist = sorted(wlist.items(), key=lambda x:x[1], reverse = True)
        jsonfile = Path(data_dir).joinpath("words.json")
        print("Write words: %s" % jsonfile)
        with open(jsonfile, "w", encoding='utf-8') as f:
            f.write(json.dumps(list(wlist), indent=2, ensure_ascii=False))

        return words

    def draw_words_cloud(self, data_dir, text):
        """
        Draw WordCloud figure for one project

        Parameters
        ----------
        data_dir : String
            Directory which have issue data
        text : String
            Text data to draw
        """
        assert data_dir.exists() and data_dir.is_dir(), "Data folder should exist."

        if (not text) or (len(text) == 0):
            print("Skip empty text")
            return
        text = ' '.join(text).replace('\n', '')

        # Japanese font
        fpath = '$HOME/Library/Fonts/ipagp.ttf'
        if os.name == 'nt':
            fpath = r'C:\Windows\Fonts\YuGothB.ttc'
        elif os.name == 'posix':
            fpath = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
        print("use japanese font: %s" % fpath)
        assert Path(fpath).exists(), ("Japanese font should exist. %s" % fpath)

        # Read the stop words not to show on image.
        stop_words = []
        stop_word_file = Path("config/stopwords.txt")
        if stop_word_file.exists():
            with open(stop_word_file, 'r', encoding='utf-8') as file:
                ss = file.read()
                stop_words = ss.split('\n')

        # Create the WordCloud image.
        wordcloud = WordCloud(background_color = "white",
                            font_path = fpath,
                            collocations = False,
                            width = 800,
                            height = 500,
                            stopwords=set(stop_words)).generate(text)

        # Image file path
        image_dir = Path('image')
        image_dir.mkdir(exist_ok=True)
        imagefile = image_dir.joinpath(data_dir.name + ".png")
        print("draw image: %s" % imagefile)

        # Draw the image and save it.
        plt.figure(figsize=(6, 4))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(imagefile)
        plt.close()

    def parse_and_draw_for_project(self, data_dir):
        """
        Parse text and draw WordCloud figure for one project

        Parameters
        ----------
        data_dir : String
            Directory which have issue data
        """
        assert data_dir.exists() and data_dir.is_dir(), "Data folder should exist."

        # Extract text from Redmine issues
        text = self.extract_text(data_dir)
        # Parse input text
        words = self.parse_text_data(data_dir, text)
        # Draw picture by words
        self.draw_words_cloud(data_dir, words)

    def parse_and_draw(self):
        """
        Parse text and draw WordCloud figure for all input
        """
        # Input folder
        data_dir = Path('data')
        # Search data files in the source folder
        for datafile in sorted(data_dir.glob('**/issues.pickle')):
            print("issue file: %s" % datafile)
            self.parse_and_draw_for_project(datafile.parent)

if __name__ == "__main__":
    ic = ImageCreator()
    ic.parse_and_draw()
