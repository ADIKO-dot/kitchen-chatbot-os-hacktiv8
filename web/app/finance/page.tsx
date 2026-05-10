"use client";

import { useState, useEffect } from "react";
import { calculateFoodCost, calculateMenuPrice, addWaste, getWasteSummary, getWasteWeekly } from "@/lib/api";

export default function FinancePage() {
  const [cogs, setCogs] = useState("");
  const [revenue, setRevenue] = useState("");
  const [foodCostResult, setFoodCostResult] = useState<{ food_cost_pct: number; gross_profit: number } | null>(null);

  const [costPortion, setCostPortion] = useState("");
  const [targetPct, setTargetPct] = useState("30");
  const [menuPrice, setMenuPrice] = useState<number | null>(null);

  const [wasteItem, setWasteItem] = useState("");
  const [wasteQty, setWasteQty] = useState("");
  const [wasteUnit, setWasteUnit] = useState("kg");
  const [wasteCost, setWasteCost] = useState("");
  const [wasteReason, setWasteReason] = useState("expired");
  const [wasteSummary, setWasteSummary] = useState<{ total_loss: number; entries: number; by_reason: Record<string, number> } | null>(null);
  const [wasteWeekly, setWasteWeekly] = useState<{ total_loss: number; total_entries: number; top_waste_items: { item: string; loss: number }[] } | null>(null);

  useEffect(() => {
    getWasteSummary().then(setWasteSummary).catch(() => {});
    getWasteWeekly().then(setWasteWeekly).catch(() => {});
  }, []);

  const handleFoodCost = async () => {
    if (!cogs || !revenue) return;
    setFoodCostResult(await calculateFoodCost(parseFloat(cogs), parseFloat(revenue)));
  };

  const handleMenuPrice = async () => {
    if (!costPortion || !targetPct) return;
    const r = await calculateMenuPrice(parseFloat(costPortion), parseFloat(targetPct));
    setMenuPrice(r.menu_price);
  };

  const handleAddWaste = async () => {
    if (!wasteItem || !wasteQty || !wasteCost) return;
    await addWaste(wasteItem, parseFloat(wasteQty), wasteUnit, parseFloat(wasteCost), wasteReason);
    setWasteItem(""); setWasteQty(""); setWasteCost("");
    setWasteSummary(await getWasteSummary());
    setWasteWeekly(await getWasteWeekly());
  };

  const inputClass = "w-full mt-1 bg-bg/50 border border-border rounded-japandi px-3 py-2 text-sm text-white placeholder-muted/50";
  const labelClass = "text-[11px] text-muted uppercase tracking-wider";

  return (
    <div className="p-6 overflow-y-auto h-full">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-semibold text-warm mb-1">💰 Finance & Costing</h1>
        <p className="text-sm text-muted mb-8">Food cost calculator, menu pricing, and waste tracking</p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Food Cost */}
          <div className="glass rounded-japandi p-5">
            <h2 className="text-sm font-semibold text-white mb-4">📊 Food Cost Calculator</h2>
            <div className="space-y-3">
              <div><label className={labelClass}>Cost of Goods Sold (Rp)</label>
                <input type="number" value={cogs} onChange={(e) => setCogs(e.target.value)} placeholder="5000000" className={inputClass} /></div>
              <div><label className={labelClass}>Total Revenue (Rp)</label>
                <input type="number" value={revenue} onChange={(e) => setRevenue(e.target.value)} placeholder="15000000" className={inputClass} /></div>
              <button onClick={handleFoodCost} className="w-full py-2.5 bg-accent text-white rounded-japandi text-sm font-medium hover:bg-accent-hover">Calculate</button>
              {foodCostResult && (
                <div className="bg-bg/50 rounded-japandi p-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted">Food Cost %</span>
                    <span className={`font-bold ${foodCostResult.food_cost_pct <= 35 ? "text-accent" : "text-terracotta"}`}>{foodCostResult.food_cost_pct}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted">Gross Profit</span>
                    <span className="text-accent font-bold">Rp {foodCostResult.gross_profit.toLocaleString()}</span>
                  </div>
                  <p className="text-[9px] text-muted/60">Target ideal: 28-35%</p>
                </div>
              )}
            </div>
          </div>

          {/* Menu Pricing */}
          <div className="glass rounded-japandi p-5">
            <h2 className="text-sm font-semibold text-white mb-4">🏷️ Menu Pricing</h2>
            <div className="space-y-3">
              <div><label className={labelClass}>Cost per Portion (Rp)</label>
                <input type="number" value={costPortion} onChange={(e) => setCostPortion(e.target.value)} placeholder="15000" className={inputClass} /></div>
              <div><label className={labelClass}>Target Food Cost %</label>
                <input type="number" value={targetPct} onChange={(e) => setTargetPct(e.target.value)} placeholder="30" className={inputClass} /></div>
              <button onClick={handleMenuPrice} className="w-full py-2.5 bg-accent text-white rounded-japandi text-sm font-medium hover:bg-accent-hover">Calculate Price</button>
              {menuPrice && (
                <div className="bg-bg/50 rounded-japandi p-4">
                  <div className="flex justify-between items-center">
                    <span className="text-muted text-sm">Recommended Price</span>
                    <span className="text-accent font-bold text-xl">Rp {menuPrice.toLocaleString()}</span>
                  </div>
                  <p className="text-[9px] text-muted/60 mt-2">Price = Cost ÷ (Target% ÷ 100)</p>
                </div>
              )}
            </div>
          </div>

          {/* Waste Tracker */}
          <div className="glass rounded-japandi p-5">
            <h2 className="text-sm font-semibold text-white mb-4">🗑️ Waste Tracker</h2>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div><label className={labelClass}>Item</label>
                  <input type="text" value={wasteItem} onChange={(e) => setWasteItem(e.target.value)} placeholder="Ayam" className={inputClass} /></div>
                <div><label className={labelClass}>Qty</label>
                  <div className="flex gap-1 mt-1">
                    <input type="number" value={wasteQty} onChange={(e) => setWasteQty(e.target.value)} placeholder="2"
                      className="w-full bg-bg/50 border border-border rounded-japandi px-3 py-2 text-sm text-white" />
                    <select value={wasteUnit} onChange={(e) => setWasteUnit(e.target.value)}
                      className="bg-bg/50 border border-border rounded-japandi px-2 text-sm text-white">
                      <option value="kg">kg</option><option value="pcs">pcs</option><option value="liter">L</option><option value="gram">g</option>
                    </select>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div><label className={labelClass}>Cost/Unit (Rp)</label>
                  <input type="number" value={wasteCost} onChange={(e) => setWasteCost(e.target.value)} placeholder="50000" className={inputClass} /></div>
                <div><label className={labelClass}>Reason</label>
                  <select value={wasteReason} onChange={(e) => setWasteReason(e.target.value)} className={inputClass + " mt-1"}>
                    <option value="expired">Expired</option><option value="spoiled">Spoiled</option>
                    <option value="overproduction">Overproduction</option><option value="dropped">Dropped</option>
                  </select>
                </div>
              </div>
              <button onClick={handleAddWaste} className="w-full py-2.5 bg-terracotta text-white rounded-japandi text-sm font-medium hover:bg-terracotta/80">+ Log Waste</button>
            </div>
          </div>

          {/* Waste Summary */}
          <div className="glass rounded-japandi p-5">
            <h2 className="text-sm font-semibold text-white mb-4">📈 Waste Summary</h2>
            {wasteSummary ? (
              <div className="space-y-3">
                <div className="bg-bg/50 rounded-japandi p-4">
                  <p className="text-[10px] text-muted uppercase">Today&apos;s Loss</p>
                  <p className="text-2xl font-bold text-terracotta">Rp {wasteSummary.total_loss.toLocaleString()}</p>
                  <p className="text-[10px] text-muted">{wasteSummary.entries} entries</p>
                </div>
                {wasteSummary.by_reason && Object.keys(wasteSummary.by_reason).length > 0 && (
                  <div className="bg-bg/50 rounded-japandi p-4">
                    <p className="text-[10px] text-muted uppercase mb-2">By Reason</p>
                    {Object.entries(wasteSummary.by_reason).map(([reason, loss]) => (
                      <div key={reason} className="flex justify-between text-sm py-1">
                        <span className="text-muted capitalize">{reason}</span>
                        <span className="text-terracotta">Rp {(loss as number).toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                )}
                {wasteWeekly && wasteWeekly.top_waste_items.length > 0 && (
                  <div className="bg-bg/50 rounded-japandi p-4">
                    <p className="text-[10px] text-muted uppercase mb-2">Top Waste Items</p>
                    {wasteWeekly.top_waste_items.map((item) => (
                      <div key={item.item} className="flex justify-between text-sm py-1">
                        <span className="text-muted">{item.item}</span>
                        <span className="text-terracotta">Rp {item.loss.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-muted text-sm">No waste data yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
