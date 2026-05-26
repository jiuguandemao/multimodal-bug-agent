# Evaluation Results

| Metric | Result |
|---|---:|
| Bug type accuracy | 6/6 = 100.0% |
| Top-1 suspicious file hit rate | 4/6 = 66.7% |
| Top-3 suspicious file hit rate | 6/6 = 100.0% |

| Case | Expected Type | Predicted Type | Expected File | Top-1 File | Type Hit | Top-1 | Top-3 |
|---|---|---|---|---|---:|---:|---:|
| case_01_register_500 | 接口异常 / 服务端 500 | 接口异常 / 服务端 500 | code/backend/register_service.py | code/backend/register_service.py | Y | Y | Y |
| case_02_login_timeout | 接口超时 / Loading 卡死 | 接口超时 / Loading 卡死 | code/frontend/Login.jsx | code/frontend/Login.jsx | Y | Y | Y |
| case_03_upload_failed | 上传限制异常 | 上传限制异常 | code/backend/upload_controller.py | code/frontend/Upload.jsx | Y | N | Y |
| case_04_blank_page_typeerror | 前端空值异常 / 页面白屏 | 前端空值异常 / 页面白屏 | code/frontend/Profile.jsx | code/frontend/Profile.jsx | Y | Y | Y |
| case_05_order_amount_error | 金额计算不一致 | 金额计算不一致 | code/frontend/OrderDetail.tsx | code/frontend/OrderDetail.tsx | Y | Y | Y |
| case_06_permission_403 | 权限校验异常 | 权限校验异常 | code/backend/permission.py | code/frontend/AdminUsers.jsx | Y | N | Y |
