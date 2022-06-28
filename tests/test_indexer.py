from indexer import indexIt, count_words

def test_index_it():
    chapter_links = indexIt()
    assert type(chapter_links) == list
    for link in chapter_links:
        assert link[:24] == "https://wanderinginn.com"
        assert type(link) == str

def test_count_words():
    res = count_words()
    assert type(res) == dict

