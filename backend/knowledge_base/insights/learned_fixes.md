# Learned Insights

## [2026-02-02 13:41:31] Fix for Error 202
Error 202 is fixed by rebooting the coffee machine.

## [2026-02-04 09:55:44] 高CPU使用率问题排查 - openebs-io-engine Pod
在排查TestAlert告警时，发现告警中提到的pod-123并不存在。但通过Prometheus查询发现，多个openebs-io-engine相关的Pod存在严重CPU使用率过高的问题，CPU使用率接近400%。

根本原因：
- openebs-io-engine Pod出现CPU使用率异常，可能由于存储引擎负载过高、配置问题或存储后端故障导致

影响：
- 这些Pod的高CPU使用率可能导致节点资源紧张，影响其他Pod的正常运行
- 存储性能可能受到影响，进而影响使用该存储的其他应用

修复建议：
1. 立即检查openebs-io-engine Pod的日志，查看是否有错误信息
2. 检查存储后端的状态和性能
3. 检查openebs相关配置，确认资源限制是否合理
4. 考虑重启有问题的Pod以暂时缓解问题
5. 检查是否有存储密集型任务导致的负载过高
6. 如问题持续，可能需要调整openebs的资源配置或排查存储后端问题

## [2026-02-04 10:10:41] TestAlert for pod-123 High CPU Usage Investigation
经过调查发现，pod-123 已经不存在于集群中，且没有找到与 TestAlert 相关的告警规则。然而，当前集群中存在一些 CPU 使用率非常高的 Pod，包括：

1. openebs-io-engine-* 系列 Pod (CPU 使用率接近 4.0)
2. cu-iot-scenario-linkage-server-66d6656945-bdgm5 (CPU 使用率 3.51)
3. cluster1-pxc-0 (CPU 使用率 3.44)
4. kafka-sasl-0 (CPU 使用率 1.46)

这些 Pod 可能是导致类似告警的潜在原因。建议检查这些高 CPU 使用率的 Pod，确认它们是否正常运行，以及是否需要调整资源限制或进行性能优化。

对于已不存在的 pod-123，可能的情况是：
1. Pod 已被重新调度或删除
2. 告警规则可能配置错误，指向了不存在的 Pod
3. 告警是历史告警，Pod 在告警发生时存在但现在已经不存在

