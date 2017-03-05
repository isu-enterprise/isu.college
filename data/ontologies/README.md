# The ontologies used in this project

 * Friend of a Friend (FOAF): an experimental linked information system http://www.foaf-project.org/ . FOAF is a computer language defining a dictionary of people-related terms that can be used in structured data (e.g. RDFa, JSON-LD, Linked Data).
 * Teaching Core  Vocabulary Specification http://linkedscience.org/vocabularies/ , RDF -  http://linkedscience.org/teach/ns/teach.rdf . TEACH, the Teaching Core Vocabulary, is a lightweight vocabulary providing terms to enable teachers to relate things in their courses together. The Teaching Core Vocabulary is based on practical requirements set by providing seminar and course descriptions as Linked Data.
 * FRAPO, the Funding, Research Administration and Projects Ontology http://www.sparontologies.net/ontologies/frapo/source.html . FRAPO, the Funding, Research Administration and Projects Ontology, is a CERIF-compliant ontology written in OWL 2 DL for describing research project administrative information. This ontology is available at http://purl.org/cerif/frapo/, and uses the namespace prefix 'frapo'.
 * This provides the base elements required by myExperiment for content management, social networking and object annotation. http://rdf.myexperiment.org/ontologies/base/ . (My comment) It suppose to be used as annotation engine in Socially networked publishing. How does it relate to Open Annotation?
 * VIVO Core Ontology (vivo) http://vivoweb.org/ .

Less useful ones are

 * Scientific People Ontology http://lod.taxonconcept.org/ontology/sci_people.owl . The ontology is not well commented.
 * Scholarly Contributions and Roles Ontology (scoro) http://www.sparontologies.net/ontologies/scoro/source.html . SCoRO, the Scholarly Contributions and Roles Ontology, is an ontology for use by authors and publishers for describing the contributions that may be made and the roles that may be held by a person with respect to a journal article or other publication, and by research administrators for describing contributions and roles with respect to other aspects of scholarly research.
 * Semantic Web Conference Ontology (swc) http://data.semanticweb.org/ns/swc/swc_2009-05-09.html . The Semantic Web Conference ontology (SWC) is an ontology for describing academic conferences. It was initially designed to support the European Semantic Web Conference, ESWC2007, and later extended for both the following conferences in the ESWC series, as well as in the ISWC series. Historically, the SWC ontology also draws heavily on ontologies developed for ESWC2006 and ISWC2006.
 * Semantic Web for Research Communities (swrc) http://ontoware.org/swrc/ . The SWRC (Semantic Web for Research Communities) is an ontology for modeling entities of research communities such as persons, organisations, publications (bibliographic metadata) and their relationships.



## Goole Introduction to Structured Data

https://developers.google.com/search/docs/guides/intro-structured-data?visit_id=1-636241996299357028-570034971&hl=en&rd=1

An example code snippet

```Javascript
<script type="application/ld+json">
{
  "@context": "http://schema.org",
  "@type": "Organization",
  "url": "http://www.your-company-site.com",
  "contactPoint": [{
    "@type": "ContactPoint",
    "telephone": "+1-401-555-1212",
    "contactType": "customer service"
  }]
}
</script>
```
