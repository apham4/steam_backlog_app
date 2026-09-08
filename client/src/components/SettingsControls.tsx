// Component displaying the controls for user settings.

import React from 'react';
import type { UserSettings } from '../types/api';
import { config } from '../config';

interface Props {
    settings: UserSettings;
    onSettingChanged: (updatedSettings: UserSettings) => void;
}

export const SettingsControls: React.FC<Props> = ({ settings, onSettingChanged }) => {
    const handleChange = (field: keyof UserSettings, minVal: number, rawVal: number) => {
        const safeVal = isNaN(rawVal) ? minVal : rawVal;
        const value = Math.max(minVal, safeVal);
        // Create a new object copy so React re-renders because of the reference change.
        onSettingChanged({ ...settings, [field]: value });
    };

    return (
        <div className="w-full max-w-xl bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-6">
            <h3 className="text-lg font-semibold text-white tracking-wide border-b border-slate-800 pb-3">
                Recommendation Preferences
            </h3>

            <div className="space-y-5">
                {/* 1. Backlog Max Playtime */}
                <div className="space-y-2">
                <div className="flex justify-between items-center text-sm">
                    <label className="text-slate-300 font-medium">
                    Backlog playtime threshold (minutes)
                    </label>
                    <input
                    type="number"
                    min={config.settingsBounds.backlogThreshold.min}
                    value={settings.backlog_threshold_mins}
                    onChange={(e) => handleChange('backlog_threshold_mins', config.settingsBounds.backlogThreshold.min, parseInt(e.target.value, 10))}
                    className="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-right text-sm text-white focus:outline-none focus:border-blue-500"
                    />
                </div>
                <input
                    type="range"
                    min={config.settingsBounds.backlogThreshold.min}
                    max={config.settingsBounds.backlogThreshold.sliderMax}
                    value={Math.min(settings.backlog_threshold_mins, config.settingsBounds.backlogThreshold.sliderMax)}
                    onChange={(e) => handleChange('backlog_threshold_mins', config.settingsBounds.backlogThreshold.min, parseInt(e.target.value, 10))}
                    className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
                <div className="flex justify-between text-[11px] text-slate-500">
                    <span>{config.settingsBounds.backlogThreshold.min}m</span>
                    <span>{config.settingsBounds.backlogThreshold.sliderMax}m+</span>
                </div>
                </div>

                {/* 2. Recently Played Min Playtime */}
                <div className="space-y-2">
                <div className="flex justify-between items-center text-sm">
                    <label className="text-slate-300 font-medium">
                    Recent activity threshold (past 2 weeks)
                    </label>
                    <input
                    type="number"
                    min={config.settingsBounds.recentThreshold.min}
                    value={settings.recent_threshold_mins}
                    onChange={(e) => handleChange('recent_threshold_mins', config.settingsBounds.recentThreshold.min, parseInt(e.target.value, 10))}
                    className="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-right text-sm text-white focus:outline-none focus:border-blue-500"
                    />
                </div>
                <input
                    type="range"
                    min={config.settingsBounds.recentThreshold.min}
                    max={config.settingsBounds.recentThreshold.sliderMax}
                    value={Math.min(settings.recent_threshold_mins, config.settingsBounds.recentThreshold.sliderMax)}
                    onChange={(e) => handleChange('recent_threshold_mins', config.settingsBounds.recentThreshold.min, parseInt(e.target.value, 10))}
                    className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
                <div className="flex justify-between text-[11px] text-slate-500">
                    <span>{config.settingsBounds.recentThreshold.min}m</span>
                    <span>{config.settingsBounds.recentThreshold.sliderMax}m+</span>
                </div>
                </div>

                {/* 3. Skip Cooldown Days */}
                <div className="space-y-2">
                <div className="flex justify-between items-center text-sm">
                    <label className="text-slate-300 font-medium">
                    Skip cooldown period (days)
                    </label>
                    <input
                    type="number"
                    min={config.settingsBounds.skipCooldown.min}
                    value={settings.skip_cooldown_days}
                    onChange={(e) => handleChange('skip_cooldown_days', config.settingsBounds.skipCooldown.min, parseInt(e.target.value, 10))}
                    className="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-right text-sm text-white focus:outline-none focus:border-blue-500"
                    />
                </div>
                <input
                    type="range"
                    min={config.settingsBounds.skipCooldown.min}
                    max={config.settingsBounds.skipCooldown.sliderMax}
                    value={Math.min(settings.skip_cooldown_days, config.settingsBounds.skipCooldown.sliderMax)}
                    onChange={(e) => handleChange('skip_cooldown_days', config.settingsBounds.skipCooldown.min, parseInt(e.target.value, 10))}
                    className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
                <div className="flex justify-between text-[11px] text-slate-500">
                    <span>{config.settingsBounds.skipCooldown.min} day</span>
                    <span>{config.settingsBounds.skipCooldown.sliderMax}+ days</span>
                </div>
                </div>
            </div>
            </div>
    );
};