# pyEssayAnalyser

## History

Date       | Version  | Comment
---------- | -------- | --------------------
23/12/2012 | v1       | sentence extraction
03/01/2013 | v2		  | keyword + sentence extraction
21/02/2013 | v3       | integrated keyword + sentence analyser

## Changes to Package Structure ()
* all analyser modules are in EssayAnalyser package
* exploitation modules moved outside EssayAnalyser package
	* se_main (bach processing)
	* pyEssayAnalyser (Flask API)
* old version moved in legacy sub-package
* third-party modules (sbd) moved into utils package

### ke_all
* removed import betweenness; replaced by networkx.algorithms.centrality.betweenness

### se_main
* moved to outside package

### se_preprocess
* changed sbd import (to reflect moved into utils)

### se_main
* moved outside EssayAnalyser package
* changed imports to reflect move
