        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "从两日用量核算备用",
  "module": "备用分钟核算",
  "caption": "备用分钟核算",
  "detail": "以 24 小时周期的 Fourier 基拟合，并保留末六小时验证；封存次日预测后按审签实测结算实耗与少备。",
  "path": "/reserves",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "airslot",
      "label": "节目时段"
    },
    {
      "name": "plan_wh",
      "label": "计划备用 Wh"
    },
    {
      "name": "fallback",
      "label": "备用源优先级"
    },
    {
      "name": "mae",
      "label": "时间验证MAE Wh"
    },
    {
      "name": "token",
      "label": "计算号"
    },
    {
      "name": "meter",
      "label": "原电表"
    },
    {
      "name": "hour",
      "label": "原小时"
    },
    {
      "name": "actual_wh",
      "label": "实耗 Wh"
    },
    {
      "name": "short_wh",
      "label": "少备 Wh"
    },
    {
      "name": "state",
      "label": "结算状态"
    }
  ],
  "layout": "split",
  "view": "grid",
  "actions": [
    {
      "name": "forecast_wh",
      "label": "计算周期用量与备量",
      "path": "/reserves/forecast-wh",
      "fields": [
        {
          "name": "airslot",
          "label": "节目编号",
          "kind": "text",
          "initial": "AIR-17"
        },
        {
          "name": "meter",
          "label": "电表",
          "kind": "text",
          "initial": "BAT-04"
        },
        {
          "name": "clear",
          "label": "计划日晴天",
          "kind": "bool",
          "initial": true
        }
      ],
      "help": "以目标小时之前的审签读数封存次日节目预测；目标小时已有同表读数时拒收。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "save_reserve",
      "label": "记录备用量评估",
      "path": "/reserves/save-reserve",
      "fields": [
        {
          "name": "code",
          "label": "备用评估单",
          "kind": "text",
          "initial": "RV-24"
        },
        {
          "name": "token",
          "label": "计算号",
          "kind": "token",
          "initial": ""
        }
      ],
      "help": "按计算锁定原电表与目标小时封存；晚到实测经审签后结算实耗与少备。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "reserves";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
