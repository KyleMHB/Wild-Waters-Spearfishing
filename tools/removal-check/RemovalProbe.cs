using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using RimWorld;
using Verse;

namespace SpearfishingRemovalProbe;

// Developer-only mod for the save-removal check (ticket 19); never shipped. With Spearfishing turned off, it loads the save
// named by -removalProbeSave=<name>, lets the game run a few hundred ticks, writes what the map kept to
// -removalProbeOut=<file> and quits. Without those arguments it does nothing. tools/removal-check/removal_check.py drives it.
[StaticConstructorOnStartup]
public static class RemovalProbe
{
    internal const int RunTicks = 600, FrameLimit = 20000;

    private static readonly string save = Arg("removalProbeSave");
    private static readonly string output = Arg("removalProbeOut");

    static RemovalProbe()
    {
        if (save == null || output == null) return;
        Log.Message("[RemovalProbe] loading save " + save); // not translated
        // Waylith skips every frame while the window is unfocused unless run-in-background is on, and Prefs.Apply resets the
        // engine flag from prefs a few frames in. The probe's save-data folder is its own, so setting the pref is safe.
        Prefs.RunInBackground = true;
        UnityEngine.Application.runInBackground = true;
        LongEventHandler.ExecuteWhenFinished(() => GameDataSaveLoader.LoadGame(save));
    }

    public static bool Active => save != null && output != null;

    private static string Arg(string name)
    {
        string prefix = "-" + name + "=";
        return Environment.GetCommandLineArgs().FirstOrDefault(a => a.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))?.Substring(prefix.Length);
    }

    internal static void Report(int ranTicks, string note)
    {
        var sb = new StringBuilder();
        sb.AppendLine("save: " + save);
        sb.AppendLine("note: " + note);
        sb.AppendLine("ticksRun: " + ranTicks);
        sb.AppendLine("activeMods: " + string.Join(", ", ModsConfig.ActiveModsInLoadOrder.Select(m => m.PackageId)));
        foreach (var map in Find.Maps)
        {
            sb.AppendLine($"map {map.uniqueID} ({map.Size.x}x{map.Size.z}):");
            var zm = map.zoneManager;
            sb.AppendLine("  zoneManager: " + (zm == null ? "NULL" : "present"));
            if (zm != null)
            {
                sb.AppendLine("  nullZonesInList: " + zm.AllZones.Count(z => z == null));
                foreach (var zone in zm.AllZones.Where(z => z != null))
                {
                    int inGrid = zone.Cells.Count(c => zm.ZoneAt(c) == zone);
                    sb.AppendLine($"  zone {zone.GetType().Name} '{zone.label}' id {zone.ID}: {zone.Cells.Count} cells, {inGrid} in zone grid, linked {zone.zoneManager == zm}");
                }
            }
            var terrain = new Dictionary<string, int>();
            foreach (var c in map.AllCells)
            {
                string d = map.terrainGrid.TerrainAt(c)?.defName ?? "null";
                terrain[d] = terrain.TryGetValue(d, out int n) ? n + 1 : 1;
            }
            sb.AppendLine("  terrain: " + string.Join(", ", terrain.OrderByDescending(p => p.Value).Select(p => $"{p.Key} {p.Value}")));
            sb.AppendLine("  components: " + string.Join(", ", map.components.Select(c => c?.GetType().Name ?? "null")));
            foreach (var pawn in map.mapPawns.FreeColonistsSpawned)
                sb.AppendLine($"  colonist {pawn.LabelShort}: job {pawn.CurJobDef?.defName ?? "none"}, equipment {pawn.equipment?.Primary?.def.defName ?? "none"}, " +
                              $"apparel {string.Join("/", pawn.apparel?.WornApparel.Select(a => a.def.defName) ?? Enumerable.Empty<string>())}, " +
                              $"inventory {string.Join("/", pawn.inventory?.innerContainer.Select(t => t.def.defName + " x" + t.stackCount) ?? Enumerable.Empty<string>())}");
            sb.AppendLine("  items: " + string.Join(", ", map.listerThings.AllThings.Where(t => t.def.category == ThingCategory.Item).GroupBy(t => t.def.defName)
                .Select(g => g.Key + " x" + g.Sum(t => t.stackCount))));
        }
        var messages = Log.Messages.ToList();
        sb.AppendLine($"log: {messages.Count(m => m.type == LogMessageType.Error)} errors, {messages.Count(m => m.type == LogMessageType.Warning)} warnings");
        foreach (var m in messages.Where(m => m.type != LogMessageType.Message))
        {
            string text = m.text.Length > 600 ? m.text.Substring(0, 600) + " ..." : m.text;
            sb.AppendLine($"  [{m.type}] x{m.repeats} {text.Replace("\r", "").Replace("\n", " | ")}");
        }
        File.WriteAllText(output, sb.ToString());
        Root.Shutdown();
    }

    internal static string Output => output;
}

// Runs the probe's clock once the save is playing. A game component is added to every loaded game, so it needs no save data.
public class RemovalProbeComponent : GameComponent
{
    private int startTick = -1, frames;
    private bool done;

    public RemovalProbeComponent(Game game)
    {
    }

    public override void GameComponentUpdate()
    {
        if (!RemovalProbe.Active || done) return;
        UnityEngine.Application.runInBackground = true;
        if (Current.ProgramState != ProgramState.Playing) return;
        frames++;
        if (startTick < 0)
        {
            startTick = Find.TickManager.TicksGame;
            Find.TickManager.CurTimeSpeed = TimeSpeed.Superfast;
        }
        int ran = Find.TickManager.TicksGame - startTick;
        if (ran < RemovalProbe.RunTicks && frames < RemovalProbe.FrameLimit) return;
        done = true;
        try
        {
            RemovalProbe.Report(ran, ran < RemovalProbe.RunTicks ? "frame limit reached first" : "ok"); // not translated
        }
        catch (Exception e)
        {
            File.WriteAllText(RemovalProbe.Output + ".error", e.ToString());
            Root.Shutdown();
        }
    }
}
