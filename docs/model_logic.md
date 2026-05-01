# 발전량 및 경제성 계산 로직

## 1. 설비용량

설비용량은 설치 가능한 면적과 모듈 효율을 기반으로 계산한다.

```text
capacity_kwp = roof_area_m2 × roof_usage_ratio × module_efficiency
```

이때 1m²당 STC 기준 1kW의 일사 입력을 가정한다. 면적과 모듈효율은 설비용량 산정에 한 번만 사용하며, 이후 발전량 계산에서 중복 적용하지 않는다.

## 2. 발전량

```text
monthly_generation_kwh =
    monthly_ghi_kwh_m2
    × capacity_kwp
    × performance_ratio
    × orientation_factor
    × temperature_factor
```

orientation_factor는 방위각, 경사각, 음영 보정을 모두 포함한다.

## 3. 경제성

경제성은 총 설치비, 지원금, 순설치비, 자가소비 절감액, 잉여전력 수익, 유지보수비를 기반으로 계산한다.
