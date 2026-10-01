package com.iot.iotfaultdiagnosis.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "diagnosis_alternative_faults")
public class DiagnosisAlternativeFaultEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "diagnosis_record_id", nullable = false)
    private DiagnosisEntity diagnosis;

    @Column(name = "fault_id")
    private String faultId;

    @Column(name = "title")
    private String title;

    @Column(name = "similarity")
    private Double similarity;

    public DiagnosisAlternativeFaultEntity() {
    }

    public DiagnosisAlternativeFaultEntity(String faultId, String title, Double similarity) {
        this.faultId = faultId;
        this.title = title;
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

    public String getFaultId() {
        return faultId;
    }

    public void setFaultId(String faultId) {
        this.faultId = faultId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public Double getSimilarity() {
        return similarity;
    }

    public void setSimilarity(Double similarity) {
        this.similarity = similarity;
    }
}
