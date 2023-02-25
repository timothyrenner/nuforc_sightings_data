import streamlit as st
import duckdb
import pandas as pd
import altair as alt


db = duckdb.connect()
db.execute(
    """
    CREATE TABLE nuforc_reports AS
    SELECT * FROM "data/processed/nuforc_reports.csv"
    """
)


def get_date_time_counts() -> pd.DataFrame:
    return db.query(
        """
        SELECT
            DATE_TRUNC('day', date_time) AS day,
            COUNT(*) AS num_reports
        FROM
            nuforc_reports
        WHERE date_time IS NOT NULL
        GROUP BY day
        """
    ).fetchdf()


def get_recent_date_time_counts() -> pd.DataFrame:
    return db.query(
        """
        SELECT
            DATE_TRUNC('day', date_time) AS day,
            COUNT(*) AS num_reports
        FROM
            nuforc_reports
        WHERE 
            date_time IS NOT NULL AND 
            ((CURRENT_DATE - day) < 100)
        GROUP BY day
    """
    ).fetchdf()


def get_posted_counts() -> pd.DataFrame:
    return db.query(
        """
        SELECT
            DATE_TRUNC('day', posted) AS day,
            COUNT(*) AS num_reports
        FROM
            nuforc_reports
        WHERE posted IS NOT NULL
        GROUP BY day
    """
    ).fetchdf()


def get_recent_posted_counts() -> pd.DataFrame:
    return db.query(
        """
        SELECT
            DATE_TRUNC('day', posted) AS day,
            COUNT(*) AS num_reports
        FROM
            nuforc_reports
        WHERE 
            posted IS NOT NULL AND 
            ((CURRENT_DATE - day) < 100)
        GROUP BY day
    """
    ).fetchdf()


def get_shape_counts() -> pd.DataFrame:
    return db.query(
        """
        SELECT
            COALESCE(shape, 'none') AS shape,
            COUNT(*) AS num_reports
        FROM
            nuforc_reports
        GROUP BY 1
        """
    ).fetchdf()


def get_recent_shape_counts() -> pd.DataFrame:
    return db.query(
        """
        SELECT
            COALESCE(shape, 'none') AS shape,
            COUNT(*) AS num_reports
        FROM
            nuforc_reports
        WHERE
            date_time IS NOT NULL AND ((current_date - date_time::DATE) < 100)
        GROUP BY 1
    """
    ).fetchdf()


def get_country_counts() -> pd.DataFrame:
    return db.query(
        """
        SELECT
            COALESCE(country, 'none') AS country,
            COUNT(*) AS num_reports
        FROM
            nuforc_reports
        GROUP BY 1
        HAVING num_reports > 1
        """
    ).fetchdf()


def get_recent_country_counts() -> pd.DataFrame:
    return db.query(
        """
        SELECT
            COALESCE(country, 'none') AS country,
            COUNT(*) AS num_reports
        FROM
            nuforc_reports
        WHERE
            date_time IS NOT NULL AND ((current_date - date_time::DATE) < 100)
        GROUP BY 1
        HAVING num_reports > 1
        """
    ).fetchdf()


def get_state_counts() -> pd.DataFrame:
    return db.query(
        """
        SELECT
            COALESCE(state, 'none') AS state,
            COUNT(*) AS num_reports
        FROM
            nuforc_reports
        GROUP BY 1
        HAVING num_reports > 1
        """
    ).fetchdf()


def get_recent_state_counts() -> pd.DataFrame:
    return db.query(
        """
        SELECT
            COALESCE(state, 'none') AS state,
            COUNT(*) AS num_reports
        FROM
            nuforc_reports
        WHERE
            date_time IS NOT NULL AND ((current_date - date_time::DATE) < 100)
        GROUP BY 1
        HAVING num_reports > 1
        """
    ).fetchdf()


def get_geos() -> pd.DataFrame:
    return db.query(
        """
        SELECT DISTINCT
            city_latitude AS latitude,
            city_longitude AS longitude,
        FROM
            nuforc_reports
        WHERE 
            latitude IS NOT NULL AND 
            longitude IS NOT NULL
        """
    ).fetchdf()


def make_date_time_counts_chart(
    date_time_counts: pd.DataFrame, title: str = "date_time counts"
) -> alt.Chart:
    return (
        alt.Chart(date_time_counts)
        .mark_line()
        .encode(
            x=alt.X(field="day", type="temporal", title="date_time day"),
            y=alt.Y(field="num_reports", type="quantitative"),
        )
        .properties(title=title)
    )


def make_posted_counts_chart(
    posted_counts: pd.DataFrame, title: str = "posted counts"
) -> alt.Chart:

    return (
        alt.Chart(posted_counts)
        .mark_line()
        .encode(
            x=alt.X(field="day", type="temporal", title="posted day"),
            y=alt.Y(field="num_reports", type="quantitative"),
        )
        .properties(title=title)
    )


def make_shape_counts_chart(
    shape_counts: pd.DataFrame, title: str = "shape counts"
) -> alt.Chart:
    return (
        alt.Chart(shape_counts)
        .mark_bar()
        .encode(
            x=alt.X(
                field="shape",
                type="nominal",
                sort=alt.Sort(field="num_reports"),
            ),
            y=alt.Y(field="num_reports", type="quantitative"),
        )
        .properties(title=title)
    )


def make_country_counts_chart(
    country_counts: pd.DataFrame, title: str = "country counts"
) -> alt.Chart:
    return (
        alt.Chart(country_counts)
        .mark_bar()
        .encode(
            x=alt.X(
                field="country",
                type="nominal",
                sort=alt.Sort(field="num_reports"),
            ),
            y=alt.Y(field="num_reports", type="quantitative"),
        )
        .properties(title=title)
    )


def make_state_counts_chart(
    state_counts: pd.DataFrame, title: str = "state counts"
) -> alt.Chart:
    return (
        alt.Chart(state_counts)
        .mark_bar()
        .encode(
            x=alt.X(
                field="state",
                type="nominal",
                sort=alt.Sort(field="num_reports"),
            ),
            y=alt.Y(field="num_reports", type="quantitative"),
        )
        .properties(title=title)
    )


sample_frame = db.query(
    """
        SELECT * 
        FROM nuforc_reports
        WHERE posted IS NOT NULL
        ORDER BY posted DESC
        LIMIT 100
    """
).to_df()


num_records = db.query("SELECT COUNT(*) FROM nuforc_reports").fetchone()[0]

date_time_counts = get_date_time_counts()
date_time_counts_chart = make_date_time_counts_chart(date_time_counts)
recent_date_time_counts = get_recent_date_time_counts()
recent_date_time_counts_chart = make_date_time_counts_chart(
    recent_date_time_counts, title="date_time counts (recent)"
)

posted_counts = get_posted_counts()
posted_counts_chart = make_posted_counts_chart(posted_counts)
recent_posted_counts = get_recent_posted_counts()
recent_posted_counts_chart = make_posted_counts_chart(
    recent_posted_counts, title="posted counts (recent)"
)

shape_counts = get_shape_counts()
shape_counts_chart = make_shape_counts_chart(shape_counts)
recent_shape_counts = get_recent_shape_counts()
recent_shape_counts_chart = make_shape_counts_chart(
    recent_shape_counts, title="shape counts (recent)"
)

country_counts = get_country_counts()
country_counts_chart = make_country_counts_chart(country_counts)
recent_country_counts = get_recent_country_counts()
recent_country_counts_chart = make_country_counts_chart(
    recent_country_counts, title="country counts (recent)"
)

state_counts = get_state_counts()
state_counts_chart = make_state_counts_chart(state_counts)
recent_state_counts = get_recent_state_counts()
recent_state_counts_chart = make_state_counts_chart(
    recent_state_counts, title="state counts (recent)"
)

geos = get_geos()

st.title("NUFORC PULL QA")
st.write(sample_frame)
st.markdown(f"## Number of records: {num_records}")
# Map.
st.map(geos)
# Timeline chart - date_time.
st.altair_chart(date_time_counts_chart, use_container_width=True)
st.altair_chart(recent_date_time_counts_chart, use_container_width=True)
# Timeline chart - posted.
st.altair_chart(posted_counts_chart, use_container_width=True)
st.altair_chart(recent_posted_counts_chart, use_container_width=True)
# Bar chart of shapes.
st.altair_chart(shape_counts_chart, use_container_width=True)
st.altair_chart(recent_shape_counts_chart, use_container_width=True)
# Bar chart of country.
st.altair_chart(country_counts_chart, use_container_width=True)
st.altair_chart(recent_country_counts_chart, use_container_width=True)
# Bar chart of state.
st.altair_chart(state_counts_chart, use_container_width=True)
st.altair_chart(recent_state_counts_chart, use_container_width=True)
