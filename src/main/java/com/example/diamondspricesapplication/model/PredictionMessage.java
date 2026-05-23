package com.example.diamondspricesapplication.model;

public class PredictionMessage {
    private Integer iteration;
    private Integer batch_percent;
    private Integer batch_size;
    private Double rmse;
    private Double r2;
    private Double avg_predicted_price;

    public PredictionMessage() {
    }

    public Integer getIteration() {
        return iteration;
    }

    public void setIteration(Integer iteration) {
        this.iteration = iteration;
    }

    public Integer getBatch_percent() {
        return batch_percent;
    }

    public void setBatch_percent(Integer batch_percent) {
        this.batch_percent = batch_percent;
    }

    public Integer getBatch_size() {
        return batch_size;
    }

    public void setBatch_size(Integer batch_size) {
        this.batch_size = batch_size;
    }

    public Double getRmse() {
        return rmse;
    }

    public void setRmse(Double rmse) {
        this.rmse = rmse;
    }

    public Double getR2() {
        return r2;
    }

    public void setR2(Double r2) {
        this.r2 = r2;
    }

    public Double getAvg_predicted_price() {
        return avg_predicted_price;
    }

    public void setAvg_predicted_price(Double avg_predicted_price) {
        this.avg_predicted_price = avg_predicted_price;
    }
}
