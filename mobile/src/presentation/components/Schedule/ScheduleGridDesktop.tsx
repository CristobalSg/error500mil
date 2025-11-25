import { Table } from "antd";
import type { ColumnsType } from "antd/es/table";
import { DIAS, DIA_LABELS, HORAS, type ScheduleEventDetailsMap } from "../../types/schedule";
import type { Events } from "../../types/schedule";

interface Props {
  events: Events;
  details?: ScheduleEventDetailsMap;
  onCellClick: (day: string, hour: string) => void;
}

interface RowData {
  key: string;
  hora: string;
}

export default function ScheduleGridDesktop({ events, details = {}, onCellClick }: Props) {
  const HOUR_COL_WIDTH = 5;

  const columns: ColumnsType<RowData> = [
    {
      title: "Hora",
      dataIndex: "hora",
      key: "hora",
      align: "center",
      width: HOUR_COL_WIDTH,
      fixed: "left",
      onHeaderCell: () => ({
        style: { width: HOUR_COL_WIDTH, maxWidth: HOUR_COL_WIDTH },
      }),
      onCell: () => ({
        style: { width: HOUR_COL_WIDTH, maxWidth: HOUR_COL_WIDTH },
      }),
    },
    ...DIAS.map((day) => ({
      title: DIA_LABELS[day],
      key: day,
      align: "center" as const,
      render: (_: any, record: RowData) => {
        const evts = events[day]?.[record.hora];
        return (
          <button
            className={`w-full text-left rounded p-2 focus:outline-none focus:ring whitespace-normal break-words
              ${evts?.length ? "bg-pink-100" : "bg-white hover:bg-gray-50"}`}
            onClick={() => onCellClick(day, record.hora)}
          >
            {evts?.length ? evts.map((evtId) => details[evtId]?.code ?? evtId).join(", ") : (
              <span className="text-gray-400 text-sm">—</span>
            )}
          </button>
        );
      },
    })),
  ];

  const data = HORAS.map((hora) => ({ key: hora, hora }));

  return (
    <div className="hidden md:block">
      <Table
        size="small"
        pagination={false}
        columns={columns}
        dataSource={data}
        bordered
        scroll={{ x: 700 }}
        tableLayout="fixed"
        className="[&_.ant-table]:rounded-lg"
      />
    </div>
  );
}