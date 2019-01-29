# CSIndexbr

CSIndexbr (https://csindexbr.org) provides transparent data about Brazilian scientific production in Computer Science. We index full research papers published in selected conferences and journals. The papers are retrieved from DBLP.

# Input files:

* [research-areas-config.csv] (https://github.com/aserg-ufmg/CSIndex/blob/master/data/research-areas-config.csv): list of research areas covered by CSIndexbr. This file has with two columns: research area code (e.g., se) and minimum size of the conference papers indexed in this area (e.g., 10).

# Scripts 

**All these script must be called from data folder:**

* *./run se pl chi*: update the papers (and related data) for the listed research areas (se, pl, and chi, in the example). 

* *./runall*: update the papers (and related data) for **all** research areas

* *./rundblp*: download dblp files (xml, with papers) for **all** tracked professors

* *./runcitations*: update citations for for **all** research areas
