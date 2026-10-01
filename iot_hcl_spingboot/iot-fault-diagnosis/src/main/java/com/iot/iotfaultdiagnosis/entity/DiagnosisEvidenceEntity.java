package com.iot.iotfaultdiagnosis.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "diagnosis_evidence")
public class DiagnosisEvidenceEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "diagnosis_record_id", nullable = false)
    private DiagnosisEntity diagnosis;

    @Column(name = "type")
    private String type;

    @Column(name = "parameter")
    private String parameter;

    @Column(name = "reading_value")
    private Double value;

    @Column(name = "unit")
    private String unit;

    @Column(name = "status")
    private String status;

    public DiagnosisEvidenceEntity() {
    }

    public DiagnosisEvidenceEntity(String type, String parameter, Double value, String unit, String status) {
        this.type = type;
        this.parameter = parameter;
        this.value = value;
        this.unit = unit;
        this.status = status;
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

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getParameter() {
        return parameter;
    }

    public void setParameter(String parameter) {
        this.parameter = parameter;
    }

    public Double getValue() {
        return value;
    }

    public void setValue(Double value) {
        this.value = value;
    }

    public String getUnit() {
        return unit;
    }

    public void setUnit(String unit) {
        this.unit = unit;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
