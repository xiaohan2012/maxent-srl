#! /bin/bash

ROOT=/cs/fs/home/hxiao/code/CoreNLP
if [ -z $1 ]; then
	echo '`filelist` should be given as $1 '
	exit 1
fi

if [ -z $2 ]; then
	echo '`outputDirectory` should be given as $2 '
	exit 1
fi

java -cp $ROOT/classes/:$ROOT/data/stanford-corenlp-models-current.jar edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,depparse -filelist $1 -outputDirectory $2
