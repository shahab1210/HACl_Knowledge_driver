package com.iot.iotfaultdiagnosis.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "diagnosis_knowledge_sources")
public class DiagnosisKnowledgeSourceEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "diagnosis_record_id", nullable = false)
    private DiagnosisEntity diagnosis;

    @Column(name = "rank_order")
    private Integer rank;

    @Column(name = "document_id")
    private String documentId;

    @Column(name = "chunk_id")
    private String chunkId;

    @Column(name = "title")
    private String title;

    @Column(name = "source", length = 500)
    private String source;

    @Column(name = "similarity")
    private Double similarity;

    public DiagnosisKnowledgeSourceEntity() {
    }

    public DiagnosisKnowledgeSourceEntity(Integer rank, String documentId, String chunkId, String title, String source, Double similarity) {
        this.rank = rank;
        this.documentId = documentId;
        this.chunkId = chunkId;
        this.title = title;
        this.source = source;
        this.similarity = similarity;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public DiagnosisEntity getDiagnosis() {
        return diagnosis;
    }

    public void setDiagnosis(DiagnosisEntity diagnosis) {
        this.diagnosis = diagnosis;
    }

    public Integer getRank() {
        return rank;
    }

    public void setRank(Integer rank) {
        this.rank = rank;
    }

    public String getDocumentId() {
        return documentId;
    }

    public void setDocumentId(String documentId) {
        this.documentId = documentId;
    }

    public String getChunkId() {
        return chunkId;
    }

    public void setChunkId(String chunkId) {
        this.chunkId = chunkId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public Double getSimilarity() {
        return similarity;
    }

    public void setSimilarity(Double similarity) {
        this.similarity = similarity;
    }
}
