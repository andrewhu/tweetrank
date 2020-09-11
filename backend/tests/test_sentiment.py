
import sentiment

def test_sentiment():
    analyzer = sentiment.VaderSentiment
    pos_sentence = "I love Obama!"
    neg_sentence = "I hate everything!"

    assert analyzer.get_sentiment(pos_sentence) > 0
    assert analyzer.get_sentiment(neg_sentence) < 0
