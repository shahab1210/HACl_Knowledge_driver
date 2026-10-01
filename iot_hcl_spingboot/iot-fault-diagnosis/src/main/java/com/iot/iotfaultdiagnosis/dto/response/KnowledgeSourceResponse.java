package com.iot.iotfaultdiagnosis.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class KnowledgeSourceResponse {

    private Integer rank;
    private String documentId;
    private String chunkId;
    private String title;
    private String source;
    private Double similarity;

    public KnowledgeSourceResponse() {
    }

    public KnowledgeSourceResponse(Integer rank, String documentId, String chunkId, String title, String source, Double similarity) {
        this.rank = rank;
        this.documentId = documentId;
        this.chunkId = chunkId;
        this.title = title;
        this.source = source;
        this.similarity = similarity;
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
