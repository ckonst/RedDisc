import epicbot
import os
import praw
import unittest

from dotenv import load_dotenv

class HelperFunctionsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        ID = os.getenv('CLIENT_ID')
        SECRET = os.getenv('CLIENT_SECRET')
        cls.reddit = praw.Reddit(client_id=ID,
                                client_secret=SECRET,
                                user_agent="EpicBot for Reddit")

    def test_create_user_embed(self):
        embed = epicbot.create_user_embed(self.reddit.redditor('Holofan4life'))
        assert embed != None

    def test_create_empty_user_embed(self):
        embed = epicbot.create_empty_user_embed(None)
        assert embed != None

    def test_create_submission_embed(self):
        embed = epicbot.create_submission_embed(self.reddit.submission('2gmzqe'))
        assert embed != None

    def test_create_body_embed(self):
        embed = epicbot.create_body_embed(self.reddit.submission('2gmzqe'))
        assert embed != None

    def test_create_comment_embed(self):
        embed = epicbot.create_comment_embed(self.reddit.submission('2gmzqe'))
        assert embed != None

    def test_create_help_embed(self):
        embed = epicbot.create_help_embed()
        assert embed != None

    def test_sub_exists(self):
        exists = epicbot.sub_exists('dogs')
        assert exists == True
        exists = epicbot.sub_exists('qplplqrp')
        assert exists == False

    def test_user_exists(self):
        exists = epicbot.user_exists(self.reddit.redditors.search('Holofan4life'))
        assert exists == True
        exists = epicbot.user_exists(None)
        assert exists == False

    def test_to_query_string(self):
        query_string = epicbot.to_query_string(['1', '2', '3', '4'])
        assert query_string == '1 2 3 4'

    def test_is_image(self):
        is_image = epicbot.is_image('https://imgur.com/LG4Jmfa.jpg')
        assert is_image
        is_image = epicbot.is_image('https://imgur.com/LG4Jmfa')
        assert not is_image
    
    def test_url_morph(self):
        url = epicbot.url_morph('https://i.imgur.com/A8POP2d.gifv')
        assert url == 'https://i.imgur.com/A8POP2d.gif'
        url = epicbot.url_morph('https://imgur.com/LG4Jmfa')
        assert url == 'https://imgur.com/LG4Jmfa.jpg'

    def test_extract_command_info(self):
        sort_by, lim = epicbot.extract_command_info('top10')
        assert sort_by == 'top'
        assert lim == 10
        sort_by, lim = epicbot.extract_command_info('hot')
        assert sort_by == 'hot'
        assert lim > 0

    def test_extract_options(self):
        args, kwargs = epicbot.extract_options([
            'search10', 'cats', '-all', '-top', '-alltime'])
        assert args == ['search10', 'cats']
        assert kwargs == ['all', 'top', 'alltime']
        args, kwargs = epicbot.extract_options(['top3', 'programming'])
        assert args == ['top3', 'programming']
        assert kwargs == []

if __name__ == '__main__':
    unittest.main()
    