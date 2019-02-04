# CSIndexbr

CSIndexbr (https://csindexbr.org) provides transparent data about Brazilian scientific production in Computer Science. We index full research papers published in selected conferences and journals. The papers are retrieved from DBLP.

# Scripts 

**All these script must be called from "data" folder:**

* *./run se pl chi*: update the papers (and related data) for the listed research areas (se, pl, and chi, in the example). 

* *./runall*: update the papers (and related data) for **all** research areas

* *./rundblp*: download dblp files (xml, with papers) for **all** tracked professors

* *./runcitations*: update citations for for **all** research areas

# Input files

** These files must be placed in the "data" folder: **

There are two "global" configuration files:

* [all-researchers.csv](https://github.com/aserg-ufmg/CSIndex/blob/master/data/all-researchers.csv): Brazilian CS professors (i.e., from CS departments) whose papers are tracked by CSIndexber, with three columns:

  * Professor name (do not use "-" or accents in names)
  * University (do not use distinct names for the same university; e.g. PUC-Rio and PUC-RIO)
  * DBLP PID (see in this [screenshot](https://github.com/aserg-ufmg/CSIndex/blob/master/figs/dblp-pid-screenshot.jpg) how to retrieve PIDs from DBLP profiles)
  
* [research-areas-config.csv](https://github.com/aserg-ufmg/CSIndex/blob/master/data/research-areas-config.csv): research areas covered by CSIndexbr, with two columns: 
  * research area acronym (e.g., se)
  * minimum size of the conference papers indexed in this area (e.g., 10).

The following files are specific of a given research area (i.e., each area has all files listed next; although, in this list, we are using "se" as example):

* [se-confs.csv](https://github.com/aserg-ufmg/CSIndex/blob/master/data/se-confs.csv): conferences and journals indexed in a given research area ("se", in this case), with three columns: 

  * venue name at DBLP:
    * for conferences, use "booktitle" XML entry, see [example](https://dblp.uni-trier.de/rec/xml/conf/esem/CoelhoVSS18.xml); 
    * for journals, use "journal" XML entry; see [example](https://dblp.uni-trier.de/rec/xml/journals/jss/BritoHVR18.xml)
  * venue name in the charts and tables generated by CSIndexbr
  * venue type, as follows:

    * 1: top-conference 
    * 2: not used anynore
    * 3: "regular" conference (i.e., non-top)
    * 4: top-journal 
    * 5: "regular" journal (i.e., non-top)
    * 6: magazine or journal that accept short papers (>= 6 pages)
    * 7: journals with low normalized-h5-index (see [FAQ](https://csindexbr.org/faq.html), for details) 

* [se-black-list.txt](https://github.com/aserg-ufmg/CSIndex/blob/master/data/se-black-list.txt): list of papers that **must not** be indexed, although they attend the basic indexing criteria. For example, they are papers published in other tracks, that is not the main research track of a conference. Each line contains the "url" XML field of the paper (see [example](https://dblp.uni-trier.de/rec/xml/conf/icse/NetoCLGM13.xml))

* [se-white-list.txt](https://github.com/aserg-ufmg/CSIndex/blob/master/data/se-white-list.txt): list of papers that **must**  be indexed. For example, papers that do not have page numbers at DBLP metadata (see [example](https://dblp.uni-trier.de/rec/xml/journals/smr/SilvaVBAE17.xml))

# Output files

** These files are generated in the "data" folder: **

Examples assuming "se" research area:

* [se-out-confs.csv](https://github.com/aserg-ufmg/CSIndex/blob/master/data/se-out-confs.csv): number of papers in indexed conferences
* [se-out-journals.csv](https://github.com/aserg-ufmg/CSIndex/blob/master/data/se-out-journals.csv): number of papers in indexed journals
* [se-out-profs-list.csv](https://github.com/aserg-ufmg/CSIndex/blob/master/data/se-out-profs-list.csv): professores with indexed papers in the area (and their departments)
* [se-out-profs.csv](https://github.com/aserg-ufmg/CSIndex/blob/master/data/se-out-profs.csv): number of professores with indexeded papers (in the area) per department
* [se-out-scores.csv](https://github.com/aserg-ufmg/CSIndex/blob/master/data/se-out-scores.csv): department scores (see formula in the [FAQ](https://csindexbr.org/faq.html))
* [se-out-papers.csv](https://github.com/aserg-ufmg/CSIndex/blob/master/data/se-out-papers.csv): metadata about indexed papers: year, venue, title, deparments, authors, doi, top or null (otherwise), journal (J) or conference (C), arxiv url or no_arxiv (otherwise), and number of citations
