@echo OFF
isort WordnikDictionary
black WordnikDictionary --exclude "all_words.py"