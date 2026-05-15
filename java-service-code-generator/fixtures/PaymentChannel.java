package com.capte.nobe.payment.model;

import com.mybatisflex.annotation.Id;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

/**
 * 支付通道。
 */
public class PaymentChannel {

    /**
     * 主键 ID
     */
    @Id
    private Long id;

    /**
     * 通道编码
     */
    @NotBlank
    @Schema(description = "通道编码")
    private String channelCode;

    /**
     * 通道名称
     */
    @NotBlank
    @Schema(description = "通道名称")
    private String channelName;

    /**
     * 是否启用
     */
    @NotNull
    @Schema(description = "是否启用")
    private Boolean enabled;
}
