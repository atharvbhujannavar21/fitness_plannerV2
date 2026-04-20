<script>
  export let profile;

  $: bmi = Number((profile.weight / ((profile.height / 100) * (profile.height / 100))).toFixed(1));
  $: status = bmi < 18.5 ? 'Underweight' : bmi < 25 ? 'Healthy' : bmi < 30 ? 'Overweight' : 'High';
</script>

<div class="glass-panel rounded-[2rem] p-6">
  <div class="mb-5 flex items-center justify-between">
    <div>
      <p class="text-sm text-stone-400">BMI Snapshot</p>
      <h2 class="font-display text-2xl">Body Metrics</h2>
    </div>
    <div class="rounded-full bg-ember/15 px-3 py-1 text-sm text-amber-200">{status}</div>
  </div>

  <div class="flex items-end gap-4">
    <div class="font-display text-6xl font-bold">{bmi}</div>
    <div class="pb-3 text-sm text-stone-400">kg/m² based on your current height and weight</div>
  </div>

  <div class="mt-6 h-3 rounded-full bg-white/5">
    <div class="h-full rounded-full bg-gradient-to-r from-[#ffb566] to-[#ff8c00]" style={`width: ${Math.min((bmi / 35) * 100, 100)}%`}></div>
  </div>
</div>
