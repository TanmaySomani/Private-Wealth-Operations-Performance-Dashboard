"""Interactive presentation of a fictional wealth operations reporting model."""
from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

from wealth_dashboard.pipeline import DB, SNAPSHOT

st.set_page_config(page_title='Meridian | Wealth operations', page_icon='◈', layout='wide')
st.markdown('''<style>
.stApp {background: #f6f8f7; color: #172d2a;}
.block-container {padding-top: 4rem; max-width: 1500px;}
h1, h2, h3 {letter-spacing: -0.035em; color: #163a34;}
[data-testid="stMetric"] {background: #fff; border: 1px solid #e2ebe6; border-radius: 12px; padding: 18px;}
[data-testid="stMetricLabel"] {color: #55736b;}
[data-testid="stSidebar"] {background: #153c35;}
[data-testid="stSidebar"] * {color: #f1f7f3;}
[data-testid="stSidebar"] [data-testid="stSelectbox"] input, [data-testid="stSidebar"] [data-testid="stSelectbox"] button {color: #173b34 !important;}
@media (max-width: 1600px) { [data-testid="stHorizontalBlock"] {flex-wrap: wrap;} [data-testid="stColumn"] {min-width: 200px !important;} }
.eyebrow {font-size: 0.75rem; letter-spacing: 0.15em; font-weight: 700; color: #568071; text-transform: uppercase;}
.note {background: #eaf2ec; border-left: 3px solid #6c9a79; border-radius: 5px; padding: 12px 16px; color: #294b40;}
</style>''', unsafe_allow_html=True)

if not DB.exists():
    st.error('Reporting database not found. Run `python -m wealth_dashboard.generate` and `python -m wealth_dashboard.pipeline` first.')
    st.stop()

@st.cache_data
def load(db_modified):
    with sqlite3.connect(DB) as conn:
        return {name: pd.read_sql_query(f'SELECT * FROM {name}', conn) for name in ['client_dimension', 'task_reporting', 'fee_reporting', 'fee_reconciliation', 'issues', 'load_log']}

data = load(DB.stat().st_mtime_ns)
clients, tasks, fees, recon, issues, loads = (data[k].copy() for k in ['client_dimension', 'task_reporting', 'fee_reporting', 'fee_reconciliation', 'issues', 'load_log'])
for frame, columns in [(tasks, ['created_date', 'due_date', 'completed_date']), (fees, ['fee_date']), (recon, ['fee_date'])]:
    for col in columns:
        frame[col] = pd.to_datetime(frame[col])

st.sidebar.markdown('### ◈ MERIDIAN')
st.sidebar.caption('PRIVATE WEALTH · OPERATIONS INTELLIGENCE')
page = st.sidebar.radio('Explore', ['Executive overview', 'Team & adviser scorecards', 'Client service operations', 'Reporting assurance'])
st.sidebar.markdown('---')
st.sidebar.markdown('**Scope**')
teams = ['All teams'] + sorted(clients['team_name'].dropna().unique().tolist())
team = st.sidebar.selectbox('Team', teams)
team_clients = clients if team == 'All teams' else clients[clients.team_name == team]
advisers = ['All advisers'] + sorted(team_clients['adviser_name'].dropna().unique().tolist())
adviser = st.sidebar.selectbox('Adviser', advisers)
if adviser != 'All advisers':
    team_clients = team_clients[team_clients.adviser_name == adviser]
selected_ids = set(team_clients.client_id)
months = pd.date_range('2025-04-01', SNAPSHOT, freq='MS').to_pydatetime().tolist()
start, end = st.sidebar.select_slider('Due / fee month', options=months, value=(months[0], months[-1]), format_func=lambda x: x.strftime('%b %Y'))
start, end = pd.Timestamp(start), pd.Timestamp(end) + pd.offsets.MonthEnd(0)
period_tasks = tasks[tasks.client_id.isin(selected_ids) & tasks.due_date.between(start, end)]
period_fees = fees[fees.client_id.isin(selected_ids) & fees.fee_date.between(start, end)]
# Unmatched ledger-only rows have no client and are only visible at the all-firm level.
period_recon = recon[recon.fee_date.between(start, end) & (recon.client_id.isin(selected_ids) | (recon.client_id.isna() & (team == 'All teams') & (adviser == 'All advisers')))]
all_scoped_tasks = tasks[tasks.client_id.isin(selected_ids)]
asof = pd.Timestamp(SNAPSHOT)
st.sidebar.markdown('---')
st.sidebar.caption(f'Snapshot: {SNAPSHOT}\n\nSynthetic data only · AUD')

money = lambda x: f'${x:,.0f}'
def pct(n, d):
    return f'{100*n/d:.1f}%' if d else '—'
def chart(fig):
    fig.update_layout(template='plotly_white', margin=dict(l=10, r=10, t=20, b=10), height=320, font=dict(color='#315449'), colorway=['#1d6855', '#c99752', '#9bbdaf', '#67947f'], legend_title_text='')
    st.plotly_chart(fig, use_container_width=True)
def headline(kicker, title, subtitle):
    st.markdown(f'<div class="eyebrow">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)
def show(df):
    st.dataframe(df, hide_index=True, use_container_width=True)

def completion(frame):
    eligible = frame[frame.status != 'Cancelled']
    return int(eligible.completed_on_time.sum()), len(eligible)

if page == 'Executive overview':
    headline('Management briefing', 'A clearer view of client service', 'A fictional operating model for a private wealth advisory firm · all values in AUD')
    overdue = all_scoped_tasks[(all_scoped_tasks.task_type == 'Annual review') & (all_scoped_tasks.overdue_at_snapshot == 1)]
    n, d = completion(period_tasks)
    target = 100_000 * (3 if team == 'All teams' else 1) * len(pd.date_range(start, end, freq='MS'))
    cols = st.columns(5)
    cols[0].metric('Active clients', f"{(team_clients.status == 'Active').sum():,}", help='Current client snapshot; independent of the date filter.')
    cols[1].metric('Recorded fees', money(period_fees.amount_cents.sum()/100), help='Accepted operational fees with fee dates in the selected range; before finance reconciliation.')
    cols[2].metric('Fees vs plan', f'{(period_fees.amount_cents.sum()/100/target - 1)*100:+.1f}%' if adviser == 'All advisers' and target else '—', help='Synthetic plan: $100,000 per team per month. No adviser-level plan; firm revenue includes unassigned clients.')
    cols[3].metric('Overdue reviews', f'{len(overdue):,}', help='Open annual reviews due before the snapshot; independent of the date filter.')
    cols[4].metric('On-time completion', pct(n,d), help='Completed by due date / non-cancelled tasks due in the selected range. Open and late tasks count in the denominator.')
    st.write('')
    st.markdown('<div class="note">Use the period filter for flow metrics. Client counts and overdue workloads are snapshot measures, so they remain anchored to 30 September 2026.</div>', unsafe_allow_html=True)
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader('Fee revenue over time')
        monthly = period_fees.assign(Month=period_fees.fee_date.dt.to_period('M').dt.to_timestamp()).groupby('Month', as_index=False).amount_cents.sum()
        monthly['Fees (AUD)'] = monthly.amount_cents/100
        if not monthly.empty: chart(px.area(monthly, x='Month', y='Fees (AUD)'))
        else: st.info('No fees in this selection.')
    with right:
        st.subheader('Service outcomes by due month')
        eligible = period_tasks[period_tasks.status != 'Cancelled'].copy()
        eligible['Month'] = eligible.due_date.dt.to_period('M').dt.to_timestamp()
        monthly_tasks = eligible.groupby('Month').agg(on_time=('completed_on_time','sum'), total=('task_id','count')).reset_index()
        monthly_tasks['On time (%)'] = 100*monthly_tasks.on_time/monthly_tasks.total
        if not monthly_tasks.empty: chart(px.line(monthly_tasks, x='Month', y='On time (%)', markers=True, range_y=[0, 100]))
        else: st.info('No eligible tasks in this selection.')
    st.caption('On-time outcomes include open tasks due in the selected period; quarantined source records are excluded and disclosed in Reporting assurance.')

elif page == 'Team & adviser scorecards':
    headline('Capacity & delivery', 'Where work is accumulating', 'Compare snapshot caseload and open work with outcomes for tasks due in the selected period.')
    group = ['team_name', 'adviser_name']
    base = team_clients.dropna(subset=['adviser_name']).groupby(group).agg(Clients=('client_id','nunique')).reset_index()
    opened = all_scoped_tasks[(all_scoped_tasks.status == 'Open') & all_scoped_tasks.adviser_name.notna()].groupby(group).agg(Open_tasks=('task_id','count'), Overdue=('overdue_at_snapshot','sum')).reset_index()
    eligible = period_tasks[(period_tasks.status != 'Cancelled') & period_tasks.adviser_name.notna()]
    outcomes = eligible.groupby(group).agg(Due=('task_id','count'), On_time=('completed_on_time','sum'), Median_turnaround_days=('turnaround_days','median')).reset_index()
    score = base.merge(opened, on=group, how='left').merge(outcomes, on=group, how='left').fillna({'Open_tasks':0,'Overdue':0,'Due':0,'On_time':0})
    score['On time %'] = (100*score.On_time/score.Due.replace(0, float('nan'))).round(1)
    score = score.rename(columns={'team_name':'Team', 'adviser_name':'Adviser', 'Open_tasks':'Open tasks', 'Median_turnaround_days':'Median turnaround (days)'})
    if not score.empty:
        chart(px.bar(score.sort_values('Overdue', ascending=False), x='Adviser', y='Overdue', color='Team', title='Overdue open tasks at snapshot'))
        show(score.sort_values('Overdue', ascending=False))
    else: st.info('No assigned advisers in this selection.')
    st.caption('Median turnaround uses completed tasks due in the period, measured from creation to completion. A lower number is not a quality score by itself.')

elif page == 'Client service operations':
    headline('Service queue', 'Turn insight into action', 'Prioritise overdue work, onboarding cases and upcoming reviews as at the reporting snapshot.')
    open_tasks = all_scoped_tasks[all_scoped_tasks.status == 'Open'].copy()
    open_tasks['Days overdue'] = (asof - open_tasks.due_date).dt.days.clip(lower=0)
    upcoming = open_tasks[(open_tasks.task_type == 'Annual review') & open_tasks.due_date.between(asof, asof + pd.Timedelta(days=30))]
    onboarding = open_tasks[open_tasks.task_type == 'Onboarding']
    a,b,c = st.columns(3)
    a.metric('Open tasks', len(open_tasks))
    b.metric('Open onboarding', len(onboarding))
    c.metric('Reviews due in 30 days', len(upcoming))
    st.caption('The queue is a snapshot and does not use the selected due / fee period. Future cases are shown only if present in the source extract.')
    left, right = st.columns(2)
    with left:
        st.subheader('Open onboarding by stage')
        stages = onboarding.groupby('stage', dropna=False).size().reset_index(name='Cases').rename(columns={'stage':'Stage'})
        if not stages.empty: chart(px.bar(stages, x='Stage', y='Cases'))
        else: st.info('No open onboarding cases.')
    with right:
        st.subheader('Ageing of open work')
        aged = open_tasks.copy()
        aged['Age band'] = pd.cut(aged['Days overdue'], [-1,0,30,60,10000], labels=['Not overdue','1–30 days','31–60 days','61+ days'])
        buckets = aged.groupby('Age band', observed=False).size().reset_index(name='Tasks')
        if not aged.empty: chart(px.bar(buckets, x='Age band', y='Tasks'))
        else: st.info('No open work.')
    st.subheader('Priority queue')
    queue = open_tasks.sort_values(['Days overdue','due_date'], ascending=[False,True])
    show(queue[['task_id','client_id','adviser_name','task_type','stage','due_date','Days overdue']].rename(columns={'task_id':'Task','client_id':'Client','adviser_name':'Adviser','task_type':'Type','stage':'Stage','due_date':'Due'}))

else:
    headline('Trust & controls', 'Can management rely on the numbers?', 'Review quarantined records, ownership gaps and fee differences before distributing the report.')
    exceptions = period_recon[period_recon.match_status != 'Matched']
    a,b,c,d = st.columns(4)
    a.metric('Quarantined rows', int((issues.disposition == 'Quarantined').sum()), help='Entire load, independent of filters.')
    b.metric('Ownership exceptions', int((issues.rule == 'Assigned adviser').sum()), help='Entire load, independent of filters.')
    c.metric('Fee exceptions', len(exceptions), help='Selected fee period and ownership scope. Ledger-only entries appear only for all teams.')
    d.metric('Net ledger − operations', money(period_recon.difference_cents.sum()/100), help='Signed difference across selected reconciliation rows; positive means ledger is higher.')
    st.markdown('<div class="note">Data quality checks below describe the entire load. Fee reconciliation follows your filters; unmatched finance entries have no team and appear only in the all-firm view.</div>', unsafe_allow_html=True)
    st.subheader('Fee reconciliation exceptions')
    detail = exceptions[['fee_id','client_id','fee_date','operational_cents','ledger_cents','difference_cents','match_status']].copy()
    for col in ['operational_cents','ledger_cents','difference_cents']:
        detail[col] = detail[col]/100
    show(detail.rename(columns={'fee_id':'Fee ID','client_id':'Client','fee_date':'Fee / posting date','operational_cents':'Operations ($)','ledger_cents':'Ledger ($)','difference_cents':'Difference ($)','match_status':'Finding'}))
    st.subheader('Validation register')
    show(issues[['source','record_id','rule','disposition']].rename(columns={'source':'Source','record_id':'Record','rule':'Rule','disposition':'Disposition'}))
    st.caption('The pipeline quarantines invalid rows; it does not silently correct source data. Resolve the issue in the upstream extract and rerun the load.')
    st.subheader('Latest successful load')
    show(loads[['snapshot_date','completed_at_utc','status']].rename(columns={'snapshot_date':'Business snapshot','completed_at_utc':'Loaded (UTC)','status':'Status'}))
    st.caption('Only successful local data rebuilds are recorded here. Scheduled refresh and failed-run monitoring are not implemented.')
