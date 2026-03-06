import { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState({});

  useEffect(() => {
    fetch("https://garment-erp-production.up.railway.app/dashboard/summary")
      .then(res => res.json())
      .then(setData);
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Factory Dashboard</h1>

      <h3>Today Production</h3>
      <p>{data.today_production}</p>

      <h3>Bundles In Progress</h3>
      <p>{data.bundles_in_progress}</p>

      <h3>Top Worker</h3>
      <p>
        {data.top_worker
          ? `${data.top_worker.worker_machine} (${data.top_worker.total_produced_qty})`
          : ""}
      </p>
    </div>
  );
}
