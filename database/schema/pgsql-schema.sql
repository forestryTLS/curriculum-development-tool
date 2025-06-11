--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: assessment_methods; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.assessment_methods (
    a_method_id bigint NOT NULL,
    a_method character varying(191) NOT NULL,
    weight integer NOT NULL,
    course_id bigint NOT NULL,
    pos_in_alignment bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: assessment_methods_a_method_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.assessment_methods_a_method_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: assessment_methods_a_method_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.assessment_methods_a_method_id_seq OWNED BY public.assessment_methods.a_method_id;


--
-- Name: campuses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.campuses (
    campus_id bigint NOT NULL,
    campus character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: campuses_campus_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.campuses_campus_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: campuses_campus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.campuses_campus_id_seq OWNED BY public.campuses.campus_id;


--
-- Name: course_optional_priorities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_optional_priorities (
    op_id bigint NOT NULL,
    course_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: course_programs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_programs (
    id bigint NOT NULL,
    course_id bigint NOT NULL,
    program_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    course_required integer,
    instructor_assigned integer,
    map_status integer DEFAULT 0 NOT NULL,
    note character varying(191)
);


--
-- Name: course_programs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_programs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_programs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_programs_id_seq OWNED BY public.course_programs.id;


--
-- Name: course_schedules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_schedules (
    id bigint NOT NULL,
    syllabus_id bigint NOT NULL,
    "row" integer NOT NULL,
    col integer NOT NULL,
    val text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: course_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_schedules_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_schedules_id_seq OWNED BY public.course_schedules.id;


--
-- Name: course_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_users (
    id bigint NOT NULL,
    course_id bigint NOT NULL,
    user_id bigint NOT NULL,
    permission bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: course_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_users_id_seq OWNED BY public.course_users.id;


--
-- Name: course_users_old; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_users_old (
    course_id bigint NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.courses (
    course_id bigint NOT NULL,
    course_code character varying(191) NOT NULL,
    course_num character varying(30),
    delivery_modality character(1) NOT NULL,
    year integer NOT NULL,
    semester character(2) NOT NULL,
    section character varying(20),
    course_title character varying(191) NOT NULL,
    program_id bigint,
    status integer DEFAULT '-1'::integer NOT NULL,
    assigned integer NOT NULL,
    required integer,
    type character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    standard_category_id bigint DEFAULT '1'::bigint NOT NULL,
    scale_category_id bigint DEFAULT '1'::bigint NOT NULL,
    last_modified_user character varying(191)
);


--
-- Name: courses_course_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.courses_course_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: courses_course_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.courses_course_id_seq OWNED BY public.courses.course_id;


--
-- Name: custom_assessment_methods; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.custom_assessment_methods (
    custom_method_id bigint NOT NULL,
    custom_methods character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: custom_assessment_methods_custom_method_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.custom_assessment_methods_custom_method_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: custom_assessment_methods_custom_method_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.custom_assessment_methods_custom_method_id_seq OWNED BY public.custom_assessment_methods.custom_method_id;


--
-- Name: custom_learning_activities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.custom_learning_activities (
    custom_activity_id bigint NOT NULL,
    custom_activities character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: custom_learning_activities_custom_activity_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.custom_learning_activities_custom_activity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: custom_learning_activities_custom_activity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.custom_learning_activities_custom_activity_id_seq OWNED BY public.custom_learning_activities.custom_activity_id;


--
-- Name: custom_program_learning_outcomes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.custom_program_learning_outcomes (
    id bigint NOT NULL,
    custom_plo character varying(191) NOT NULL,
    custom_program_id integer NOT NULL,
    custom_program_name character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: custom_program_learning_outcomes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.custom_program_learning_outcomes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: custom_program_learning_outcomes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.custom_program_learning_outcomes_id_seq OWNED BY public.custom_program_learning_outcomes.id;


--
-- Name: departments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.departments (
    department_id bigint NOT NULL,
    department character varying(191) NOT NULL,
    faculty_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: departments_department_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.departments_department_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: departments_department_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.departments_department_id_seq OWNED BY public.departments.department_id;


--
-- Name: faculties; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.faculties (
    faculty_id bigint NOT NULL,
    faculty character varying(191) NOT NULL,
    campus_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: faculties_faculty_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.faculties_faculty_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: faculties_faculty_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.faculties_faculty_id_seq OWNED BY public.faculties.faculty_id;


--
-- Name: failed_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.failed_jobs (
    id bigint NOT NULL,
    uuid character varying(191) NOT NULL,
    connection text NOT NULL,
    queue text NOT NULL,
    payload text NOT NULL,
    exception text NOT NULL,
    failed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: failed_jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.failed_jobs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: failed_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.failed_jobs_id_seq OWNED BY public.failed_jobs.id;


--
-- Name: invites; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.invites (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    email character varying(191) NOT NULL,
    invitation_token character varying(64),
    accepted_at timestamp with time zone,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: invites_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.invites_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: invites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.invites_id_seq OWNED BY public.invites.id;


--
-- Name: learning_activities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.learning_activities (
    l_activity_id bigint NOT NULL,
    l_activity character varying(191) NOT NULL,
    course_id bigint NOT NULL,
    l_activities_pos bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: learning_activities_l_activity_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.learning_activities_l_activity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: learning_activities_l_activity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.learning_activities_l_activity_id_seq OWNED BY public.learning_activities.l_activity_id;


--
-- Name: learning_outcomes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.learning_outcomes (
    l_outcome_id bigint NOT NULL,
    clo_shortphrase character varying(191),
    l_outcome text NOT NULL,
    course_id bigint NOT NULL,
    pos_in_alignment bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: learning_outcomes_l_outcome_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.learning_outcomes_l_outcome_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: learning_outcomes_l_outcome_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.learning_outcomes_l_outcome_id_seq OWNED BY public.learning_outcomes.l_outcome_id;


--
-- Name: mapping_scale_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mapping_scale_categories (
    mapping_scale_categories_id bigint NOT NULL,
    msc_title character varying(191) NOT NULL,
    description text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: mapping_scale_categories_mapping_scale_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.mapping_scale_categories_mapping_scale_categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: mapping_scale_categories_mapping_scale_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.mapping_scale_categories_mapping_scale_categories_id_seq OWNED BY public.mapping_scale_categories.mapping_scale_categories_id;


--
-- Name: mapping_scale_programs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mapping_scale_programs (
    map_scale_id bigint NOT NULL,
    program_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: mapping_scales; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mapping_scales (
    map_scale_id bigint NOT NULL,
    title character varying(191) NOT NULL,
    abbreviation character varying(191) NOT NULL,
    description text NOT NULL,
    colour character(7) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    mapping_scale_categories_id bigint
);


--
-- Name: mapping_scales_map_scale_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.mapping_scales_map_scale_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: mapping_scales_map_scale_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.mapping_scales_map_scale_id_seq OWNED BY public.mapping_scales.map_scale_id;


--
-- Name: migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.migrations (
    id bigint NOT NULL,
    migration character varying(191) NOT NULL,
    batch integer NOT NULL
);


--
-- Name: migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.migrations_id_seq OWNED BY public.migrations.id;


--
-- Name: okanagan_syllabi; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.okanagan_syllabi (
    id bigint NOT NULL,
    syllabus_id bigint NOT NULL,
    course_format text,
    course_overview text,
    course_description text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: okanagan_syllabi_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.okanagan_syllabi_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: okanagan_syllabi_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.okanagan_syllabi_id_seq OWNED BY public.okanagan_syllabi.id;


--
-- Name: okanagan_syllabus_resources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.okanagan_syllabus_resources (
    id bigint NOT NULL,
    title character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    id_name character varying(191) NOT NULL
);


--
-- Name: okanagan_syllabus_resources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.okanagan_syllabus_resources_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: okanagan_syllabus_resources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.okanagan_syllabus_resources_id_seq OWNED BY public.okanagan_syllabus_resources.id;


--
-- Name: optional_priorities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.optional_priorities (
    op_id bigint NOT NULL,
    subcat_id bigint NOT NULL,
    optional_priority text NOT NULL,
    year integer,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    op_subdesc bigint
);


--
-- Name: optional_priorities_old; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.optional_priorities_old (
    id bigint NOT NULL,
    course_id bigint NOT NULL,
    custom_plo character varying(191) NOT NULL,
    input_status bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: optional_priorities_old_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.optional_priorities_old_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: optional_priorities_old_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.optional_priorities_old_id_seq OWNED BY public.optional_priorities_old.id;


--
-- Name: optional_priorities_op_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.optional_priorities_op_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: optional_priorities_op_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.optional_priorities_op_id_seq OWNED BY public.optional_priorities.op_id;


--
-- Name: optional_priorities_subdescriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.optional_priorities_subdescriptions (
    op_subdesc bigint NOT NULL,
    description text NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: optional_priorities_subdescriptions_op_subdesc_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.optional_priorities_subdescriptions_op_subdesc_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: optional_priorities_subdescriptions_op_subdesc_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.optional_priorities_subdescriptions_op_subdesc_seq OWNED BY public.optional_priorities_subdescriptions.op_subdesc;


--
-- Name: optional_priority_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.optional_priority_categories (
    cat_id bigint NOT NULL,
    cat_name character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: optional_priority_categories_cat_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.optional_priority_categories_cat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: optional_priority_categories_cat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.optional_priority_categories_cat_id_seq OWNED BY public.optional_priority_categories.cat_id;


--
-- Name: optional_priority_subcategories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.optional_priority_subcategories (
    subcat_id bigint NOT NULL,
    subcat_name text NOT NULL,
    cat_id bigint NOT NULL,
    subcat_desc text,
    subcat_postamble text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: optional_priority_subcategories_subcat_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.optional_priority_subcategories_subcat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: optional_priority_subcategories_subcat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.optional_priority_subcategories_subcat_id_seq OWNED BY public.optional_priority_subcategories.subcat_id;


--
-- Name: outcome_activities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.outcome_activities (
    l_outcome_id bigint NOT NULL,
    l_activity_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: outcome_assessments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.outcome_assessments (
    l_outcome_id bigint NOT NULL,
    a_method_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: outcome_maps; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.outcome_maps (
    l_outcome_id bigint NOT NULL,
    pl_outcome_id bigint NOT NULL,
    map_scale_id bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: p_l_o_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.p_l_o_categories (
    plo_category_id bigint NOT NULL,
    plo_category character varying(191) NOT NULL,
    program_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: p_l_o_categories_plo_category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.p_l_o_categories_plo_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: p_l_o_categories_plo_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.p_l_o_categories_plo_category_id_seq OWNED BY public.p_l_o_categories.plo_category_id;


--
-- Name: password_resets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.password_resets (
    email character varying(191) NOT NULL,
    token character varying(191) NOT NULL,
    created_at timestamp with time zone
);


--
-- Name: program_learning_outcomes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.program_learning_outcomes (
    pl_outcome_id bigint NOT NULL,
    plo_shortphrase character varying(191),
    pl_outcome text NOT NULL,
    program_id bigint NOT NULL,
    plo_category_id bigint,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: program_learning_outcomes_pl_outcome_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.program_learning_outcomes_pl_outcome_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: program_learning_outcomes_pl_outcome_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.program_learning_outcomes_pl_outcome_id_seq OWNED BY public.program_learning_outcomes.pl_outcome_id;


--
-- Name: program_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.program_users (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    program_id bigint NOT NULL,
    permission bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: program_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.program_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: program_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.program_users_id_seq OWNED BY public.program_users.id;


--
-- Name: program_users_old; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.program_users_old (
    user_id bigint NOT NULL,
    program_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: programs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.programs (
    program_id bigint NOT NULL,
    program character varying(191) NOT NULL,
    faculty character varying(191),
    department character varying(191),
    level character varying(191) NOT NULL,
    status integer NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    last_modified_user character varying(191),
    campus character varying(191) DEFAULT 'Other'::character varying
);


--
-- Name: programs_program_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.programs_program_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: programs_program_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.programs_program_id_seq OWNED BY public.programs.program_id;


--
-- Name: role_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.role_user (
    role_id bigint NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles (
    id bigint NOT NULL,
    role character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: standard_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.standard_categories (
    standard_category_id bigint NOT NULL,
    sc_name character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: standard_categories_standard_category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.standard_categories_standard_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: standard_categories_standard_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.standard_categories_standard_category_id_seq OWNED BY public.standard_categories.standard_category_id;


--
-- Name: standard_scales; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.standard_scales (
    standard_scale_id bigint NOT NULL,
    scale_category_id bigint,
    title character varying(191) NOT NULL,
    abbreviation character varying(191) NOT NULL,
    description text NOT NULL,
    colour character(7) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: standard_scales_standard_scale_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.standard_scales_standard_scale_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: standard_scales_standard_scale_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.standard_scales_standard_scale_id_seq OWNED BY public.standard_scales.standard_scale_id;


--
-- Name: standards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.standards (
    standard_id bigint NOT NULL,
    standard_category_id bigint DEFAULT '1'::bigint NOT NULL,
    s_shortphrase character varying(191) NOT NULL,
    s_outcome text NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: standards_outcome_maps; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.standards_outcome_maps (
    standard_id bigint NOT NULL,
    course_id bigint NOT NULL,
    standard_scale_id bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: standards_scale_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.standards_scale_categories (
    scale_category_id bigint NOT NULL,
    name character varying(191) NOT NULL,
    description text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: standards_scale_categories_scale_category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.standards_scale_categories_scale_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: standards_scale_categories_scale_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.standards_scale_categories_scale_category_id_seq OWNED BY public.standards_scale_categories.scale_category_id;


--
-- Name: standards_standard_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.standards_standard_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: standards_standard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.standards_standard_id_seq OWNED BY public.standards.standard_id;


--
-- Name: syllabi; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.syllabi (
    id bigint NOT NULL,
    course_title character varying(191),
    course_code character varying(191),
    course_num bigint,
    delivery_modality character(1) DEFAULT 'O'::bpchar NOT NULL,
    course_term character(2),
    course_year integer,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    campus character(1) NOT NULL,
    faculty character varying(191),
    department character varying(191),
    course_instructor character varying(191) NOT NULL,
    course_location character varying(191),
    office_hours text,
    class_meeting_days character(24),
    other_instructional_staff text,
    class_start_time character varying(20),
    class_end_time character varying(20),
    learning_outcomes text,
    learning_assessments text,
    learning_activities text,
    late_policy text,
    missed_exam_policy text,
    missed_activity_policy text,
    passing_criteria text,
    learning_materials text,
    learning_resources text,
    last_modified_user character varying(191),
    course_id bigint,
    include_alignment boolean DEFAULT false NOT NULL,
    cc_license text,
    copyright boolean,
    land_acknow boolean,
    custom_resource text,
    custom_resource_title text,
    cross_listed_code text,
    cross_listed_num text,
    course_section text,
    prerequisites text,
    corequisites text
);


--
-- Name: syllabi_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.syllabi_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: syllabi_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.syllabi_id_seq OWNED BY public.syllabi.id;


--
-- Name: syllabi_programs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.syllabi_programs (
    id bigint NOT NULL,
    syllabus_id bigint NOT NULL,
    program_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: syllabi_programs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.syllabi_programs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: syllabi_programs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.syllabi_programs_id_seq OWNED BY public.syllabi_programs.id;


--
-- Name: syllabi_resources_okanagan; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.syllabi_resources_okanagan (
    id bigint NOT NULL,
    syllabus_id bigint NOT NULL,
    o_syllabus_resource_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: syllabi_resources_okanagan_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.syllabi_resources_okanagan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: syllabi_resources_okanagan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.syllabi_resources_okanagan_id_seq OWNED BY public.syllabi_resources_okanagan.id;


--
-- Name: syllabi_resources_vancouver; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.syllabi_resources_vancouver (
    id bigint NOT NULL,
    syllabus_id bigint NOT NULL,
    v_syllabus_resource_id bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: syllabi_resources_vancouver_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.syllabi_resources_vancouver_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: syllabi_resources_vancouver_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.syllabi_resources_vancouver_id_seq OWNED BY public.syllabi_resources_vancouver.id;


--
-- Name: syllabi_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.syllabi_users (
    id bigint NOT NULL,
    syllabus_id bigint NOT NULL,
    user_id bigint NOT NULL,
    permission bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: syllabi_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.syllabi_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: syllabi_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.syllabi_users_id_seq OWNED BY public.syllabi_users.id;


--
-- Name: syllabus_instructors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.syllabus_instructors (
    id bigint NOT NULL,
    syllabus_id bigint NOT NULL,
    name character varying(191) NOT NULL,
    email character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: syllabus_instructors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.syllabus_instructors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: syllabus_instructors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.syllabus_instructors_id_seq OWNED BY public.syllabus_instructors.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    name character varying(191) NOT NULL,
    email character varying(191) NOT NULL,
    email_verified_at timestamp with time zone,
    password character varying(191) NOT NULL,
    remember_token character varying(100),
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    has_temp boolean DEFAULT false NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vancouver_syllabi; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vancouver_syllabi (
    id bigint NOT NULL,
    syllabus_id bigint NOT NULL,
    course_credit bigint NOT NULL,
    office_location character varying(191),
    course_description text,
    course_contacts text,
    instructor_bio text,
    course_prereqs text,
    course_coreqs text,
    course_structure text,
    course_schedule text,
    learning_analytics text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: vancouver_syllabi_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vancouver_syllabi_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vancouver_syllabi_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vancouver_syllabi_id_seq OWNED BY public.vancouver_syllabi.id;


--
-- Name: vancouver_syllabus_resources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vancouver_syllabus_resources (
    id bigint NOT NULL,
    title character varying(191) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    id_name character varying(191) NOT NULL
);


--
-- Name: vancouver_syllabus_resources_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vancouver_syllabus_resources_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vancouver_syllabus_resources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vancouver_syllabus_resources_id_seq OWNED BY public.vancouver_syllabus_resources.id;


--
-- Name: assessment_methods a_method_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assessment_methods ALTER COLUMN a_method_id SET DEFAULT nextval('public.assessment_methods_a_method_id_seq'::regclass);


--
-- Name: campuses campus_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.campuses ALTER COLUMN campus_id SET DEFAULT nextval('public.campuses_campus_id_seq'::regclass);


--
-- Name: course_programs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_programs ALTER COLUMN id SET DEFAULT nextval('public.course_programs_id_seq'::regclass);


--
-- Name: course_schedules id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_schedules ALTER COLUMN id SET DEFAULT nextval('public.course_schedules_id_seq'::regclass);


--
-- Name: course_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_users ALTER COLUMN id SET DEFAULT nextval('public.course_users_id_seq'::regclass);


--
-- Name: courses course_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses ALTER COLUMN course_id SET DEFAULT nextval('public.courses_course_id_seq'::regclass);


--
-- Name: custom_assessment_methods custom_method_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_assessment_methods ALTER COLUMN custom_method_id SET DEFAULT nextval('public.custom_assessment_methods_custom_method_id_seq'::regclass);


--
-- Name: custom_learning_activities custom_activity_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_learning_activities ALTER COLUMN custom_activity_id SET DEFAULT nextval('public.custom_learning_activities_custom_activity_id_seq'::regclass);


--
-- Name: custom_program_learning_outcomes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_program_learning_outcomes ALTER COLUMN id SET DEFAULT nextval('public.custom_program_learning_outcomes_id_seq'::regclass);


--
-- Name: departments department_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments ALTER COLUMN department_id SET DEFAULT nextval('public.departments_department_id_seq'::regclass);


--
-- Name: faculties faculty_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.faculties ALTER COLUMN faculty_id SET DEFAULT nextval('public.faculties_faculty_id_seq'::regclass);


--
-- Name: failed_jobs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.failed_jobs ALTER COLUMN id SET DEFAULT nextval('public.failed_jobs_id_seq'::regclass);


--
-- Name: invites id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invites ALTER COLUMN id SET DEFAULT nextval('public.invites_id_seq'::regclass);


--
-- Name: learning_activities l_activity_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learning_activities ALTER COLUMN l_activity_id SET DEFAULT nextval('public.learning_activities_l_activity_id_seq'::regclass);


--
-- Name: learning_outcomes l_outcome_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learning_outcomes ALTER COLUMN l_outcome_id SET DEFAULT nextval('public.learning_outcomes_l_outcome_id_seq'::regclass);


--
-- Name: mapping_scale_categories mapping_scale_categories_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mapping_scale_categories ALTER COLUMN mapping_scale_categories_id SET DEFAULT nextval('public.mapping_scale_categories_mapping_scale_categories_id_seq'::regclass);


--
-- Name: mapping_scales map_scale_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mapping_scales ALTER COLUMN map_scale_id SET DEFAULT nextval('public.mapping_scales_map_scale_id_seq'::regclass);


--
-- Name: migrations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.migrations ALTER COLUMN id SET DEFAULT nextval('public.migrations_id_seq'::regclass);


--
-- Name: okanagan_syllabi id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.okanagan_syllabi ALTER COLUMN id SET DEFAULT nextval('public.okanagan_syllabi_id_seq'::regclass);


--
-- Name: okanagan_syllabus_resources id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.okanagan_syllabus_resources ALTER COLUMN id SET DEFAULT nextval('public.okanagan_syllabus_resources_id_seq'::regclass);


--
-- Name: optional_priorities op_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priorities ALTER COLUMN op_id SET DEFAULT nextval('public.optional_priorities_op_id_seq'::regclass);


--
-- Name: optional_priorities_old id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priorities_old ALTER COLUMN id SET DEFAULT nextval('public.optional_priorities_old_id_seq'::regclass);


--
-- Name: optional_priorities_subdescriptions op_subdesc; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priorities_subdescriptions ALTER COLUMN op_subdesc SET DEFAULT nextval('public.optional_priorities_subdescriptions_op_subdesc_seq'::regclass);


--
-- Name: optional_priority_categories cat_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priority_categories ALTER COLUMN cat_id SET DEFAULT nextval('public.optional_priority_categories_cat_id_seq'::regclass);


--
-- Name: optional_priority_subcategories subcat_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priority_subcategories ALTER COLUMN subcat_id SET DEFAULT nextval('public.optional_priority_subcategories_subcat_id_seq'::regclass);


--
-- Name: p_l_o_categories plo_category_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p_l_o_categories ALTER COLUMN plo_category_id SET DEFAULT nextval('public.p_l_o_categories_plo_category_id_seq'::regclass);


--
-- Name: program_learning_outcomes pl_outcome_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_learning_outcomes ALTER COLUMN pl_outcome_id SET DEFAULT nextval('public.program_learning_outcomes_pl_outcome_id_seq'::regclass);


--
-- Name: program_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_users ALTER COLUMN id SET DEFAULT nextval('public.program_users_id_seq'::regclass);


--
-- Name: programs program_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programs ALTER COLUMN program_id SET DEFAULT nextval('public.programs_program_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: standard_categories standard_category_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standard_categories ALTER COLUMN standard_category_id SET DEFAULT nextval('public.standard_categories_standard_category_id_seq'::regclass);


--
-- Name: standard_scales standard_scale_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standard_scales ALTER COLUMN standard_scale_id SET DEFAULT nextval('public.standard_scales_standard_scale_id_seq'::regclass);


--
-- Name: standards standard_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standards ALTER COLUMN standard_id SET DEFAULT nextval('public.standards_standard_id_seq'::regclass);


--
-- Name: standards_scale_categories scale_category_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standards_scale_categories ALTER COLUMN scale_category_id SET DEFAULT nextval('public.standards_scale_categories_scale_category_id_seq'::regclass);


--
-- Name: syllabi id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi ALTER COLUMN id SET DEFAULT nextval('public.syllabi_id_seq'::regclass);


--
-- Name: syllabi_programs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_programs ALTER COLUMN id SET DEFAULT nextval('public.syllabi_programs_id_seq'::regclass);


--
-- Name: syllabi_resources_okanagan id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_resources_okanagan ALTER COLUMN id SET DEFAULT nextval('public.syllabi_resources_okanagan_id_seq'::regclass);


--
-- Name: syllabi_resources_vancouver id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_resources_vancouver ALTER COLUMN id SET DEFAULT nextval('public.syllabi_resources_vancouver_id_seq'::regclass);


--
-- Name: syllabi_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_users ALTER COLUMN id SET DEFAULT nextval('public.syllabi_users_id_seq'::regclass);


--
-- Name: syllabus_instructors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabus_instructors ALTER COLUMN id SET DEFAULT nextval('public.syllabus_instructors_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vancouver_syllabi id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vancouver_syllabi ALTER COLUMN id SET DEFAULT nextval('public.vancouver_syllabi_id_seq'::regclass);


--
-- Name: vancouver_syllabus_resources id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vancouver_syllabus_resources ALTER COLUMN id SET DEFAULT nextval('public.vancouver_syllabus_resources_id_seq'::regclass);


--
-- Name: assessment_methods idx_42482_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assessment_methods
    ADD CONSTRAINT idx_42482_primary PRIMARY KEY (a_method_id);


--
-- Name: campuses idx_42488_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.campuses
    ADD CONSTRAINT idx_42488_primary PRIMARY KEY (campus_id);


--
-- Name: course_optional_priorities idx_42492_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_optional_priorities
    ADD CONSTRAINT idx_42492_primary PRIMARY KEY (op_id, course_id);


--
-- Name: course_programs idx_42496_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_programs
    ADD CONSTRAINT idx_42496_primary PRIMARY KEY (id);


--
-- Name: course_schedules idx_42502_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_schedules
    ADD CONSTRAINT idx_42502_primary PRIMARY KEY (id);


--
-- Name: course_users idx_42509_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_users
    ADD CONSTRAINT idx_42509_primary PRIMARY KEY (id);


--
-- Name: course_users_old idx_42514_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_users_old
    ADD CONSTRAINT idx_42514_primary PRIMARY KEY (course_id, user_id);


--
-- Name: courses idx_42518_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT idx_42518_primary PRIMARY KEY (course_id);


--
-- Name: custom_assessment_methods idx_42528_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_assessment_methods
    ADD CONSTRAINT idx_42528_primary PRIMARY KEY (custom_method_id);


--
-- Name: custom_learning_activities idx_42533_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_learning_activities
    ADD CONSTRAINT idx_42533_primary PRIMARY KEY (custom_activity_id);


--
-- Name: custom_program_learning_outcomes idx_42538_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.custom_program_learning_outcomes
    ADD CONSTRAINT idx_42538_primary PRIMARY KEY (id);


--
-- Name: departments idx_42543_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT idx_42543_primary PRIMARY KEY (department_id);


--
-- Name: faculties idx_42548_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT idx_42548_primary PRIMARY KEY (faculty_id);


--
-- Name: failed_jobs idx_42553_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.failed_jobs
    ADD CONSTRAINT idx_42553_primary PRIMARY KEY (id);


--
-- Name: invites idx_42561_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invites
    ADD CONSTRAINT idx_42561_primary PRIMARY KEY (id);


--
-- Name: learning_activities idx_42566_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learning_activities
    ADD CONSTRAINT idx_42566_primary PRIMARY KEY (l_activity_id);


--
-- Name: learning_outcomes idx_42572_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learning_outcomes
    ADD CONSTRAINT idx_42572_primary PRIMARY KEY (l_outcome_id);


--
-- Name: mapping_scale_categories idx_42580_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mapping_scale_categories
    ADD CONSTRAINT idx_42580_primary PRIMARY KEY (mapping_scale_categories_id);


--
-- Name: mapping_scale_programs idx_42586_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mapping_scale_programs
    ADD CONSTRAINT idx_42586_primary PRIMARY KEY (map_scale_id, program_id);


--
-- Name: mapping_scales idx_42590_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mapping_scales
    ADD CONSTRAINT idx_42590_primary PRIMARY KEY (map_scale_id);


--
-- Name: migrations idx_42597_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.migrations
    ADD CONSTRAINT idx_42597_primary PRIMARY KEY (id);


--
-- Name: okanagan_syllabi idx_42602_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.okanagan_syllabi
    ADD CONSTRAINT idx_42602_primary PRIMARY KEY (id);


--
-- Name: okanagan_syllabus_resources idx_42609_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.okanagan_syllabus_resources
    ADD CONSTRAINT idx_42609_primary PRIMARY KEY (id);


--
-- Name: optional_priorities idx_42614_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priorities
    ADD CONSTRAINT idx_42614_primary PRIMARY KEY (op_id);


--
-- Name: optional_priorities_old idx_42621_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priorities_old
    ADD CONSTRAINT idx_42621_primary PRIMARY KEY (id);


--
-- Name: optional_priorities_subdescriptions idx_42626_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priorities_subdescriptions
    ADD CONSTRAINT idx_42626_primary PRIMARY KEY (op_subdesc);


--
-- Name: optional_priority_categories idx_42633_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priority_categories
    ADD CONSTRAINT idx_42633_primary PRIMARY KEY (cat_id);


--
-- Name: optional_priority_subcategories idx_42638_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priority_subcategories
    ADD CONSTRAINT idx_42638_primary PRIMARY KEY (subcat_id);


--
-- Name: outcome_activities idx_42644_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outcome_activities
    ADD CONSTRAINT idx_42644_primary PRIMARY KEY (l_outcome_id, l_activity_id);


--
-- Name: outcome_assessments idx_42647_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outcome_assessments
    ADD CONSTRAINT idx_42647_primary PRIMARY KEY (l_outcome_id, a_method_id);


--
-- Name: outcome_maps idx_42650_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outcome_maps
    ADD CONSTRAINT idx_42650_primary PRIMARY KEY (l_outcome_id, pl_outcome_id);


--
-- Name: p_l_o_categories idx_42655_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p_l_o_categories
    ADD CONSTRAINT idx_42655_primary PRIMARY KEY (plo_category_id);


--
-- Name: program_learning_outcomes idx_42663_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_learning_outcomes
    ADD CONSTRAINT idx_42663_primary PRIMARY KEY (pl_outcome_id);


--
-- Name: program_users idx_42670_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_users
    ADD CONSTRAINT idx_42670_primary PRIMARY KEY (id);


--
-- Name: program_users_old idx_42675_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_users_old
    ADD CONSTRAINT idx_42675_primary PRIMARY KEY (user_id, program_id);


--
-- Name: programs idx_42679_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programs
    ADD CONSTRAINT idx_42679_primary PRIMARY KEY (program_id);


--
-- Name: role_user idx_42686_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_user
    ADD CONSTRAINT idx_42686_primary PRIMARY KEY (role_id, user_id);


--
-- Name: roles idx_42690_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT idx_42690_primary PRIMARY KEY (id);


--
-- Name: standard_categories idx_42695_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standard_categories
    ADD CONSTRAINT idx_42695_primary PRIMARY KEY (standard_category_id);


--
-- Name: standard_scales idx_42700_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standard_scales
    ADD CONSTRAINT idx_42700_primary PRIMARY KEY (standard_scale_id);


--
-- Name: standards idx_42707_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standards
    ADD CONSTRAINT idx_42707_primary PRIMARY KEY (standard_id);


--
-- Name: standards_outcome_maps idx_42714_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standards_outcome_maps
    ADD CONSTRAINT idx_42714_primary PRIMARY KEY (standard_id);


--
-- Name: standards_scale_categories idx_42719_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standards_scale_categories
    ADD CONSTRAINT idx_42719_primary PRIMARY KEY (scale_category_id);


--
-- Name: syllabi idx_42726_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi
    ADD CONSTRAINT idx_42726_primary PRIMARY KEY (id);


--
-- Name: syllabi_programs idx_42735_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_programs
    ADD CONSTRAINT idx_42735_primary PRIMARY KEY (id);


--
-- Name: syllabi_resources_okanagan idx_42740_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_resources_okanagan
    ADD CONSTRAINT idx_42740_primary PRIMARY KEY (id);


--
-- Name: syllabi_resources_vancouver idx_42745_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_resources_vancouver
    ADD CONSTRAINT idx_42745_primary PRIMARY KEY (id);


--
-- Name: syllabi_users idx_42750_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_users
    ADD CONSTRAINT idx_42750_primary PRIMARY KEY (id);


--
-- Name: syllabus_instructors idx_42756_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabus_instructors
    ADD CONSTRAINT idx_42756_primary PRIMARY KEY (id);


--
-- Name: users idx_42761_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT idx_42761_primary PRIMARY KEY (id);


--
-- Name: vancouver_syllabi idx_42769_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vancouver_syllabi
    ADD CONSTRAINT idx_42769_primary PRIMARY KEY (id);


--
-- Name: vancouver_syllabus_resources idx_42776_primary; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vancouver_syllabus_resources
    ADD CONSTRAINT idx_42776_primary PRIMARY KEY (id);


--
-- Name: idx_42482_assessment_methods_course_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42482_assessment_methods_course_id_foreign ON public.assessment_methods USING btree (course_id);


--
-- Name: idx_42492_course_optional_priorities_course_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42492_course_optional_priorities_course_id_foreign ON public.course_optional_priorities USING btree (course_id);


--
-- Name: idx_42496_course_programs_course_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42496_course_programs_course_id_foreign ON public.course_programs USING btree (course_id);


--
-- Name: idx_42496_course_programs_program_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42496_course_programs_program_id_foreign ON public.course_programs USING btree (program_id);


--
-- Name: idx_42502_course_schedules_syllabus_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42502_course_schedules_syllabus_id_foreign ON public.course_schedules USING btree (syllabus_id);


--
-- Name: idx_42509_course_userss_course_id_user_id_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_42509_course_userss_course_id_user_id_unique ON public.course_users USING btree (course_id, user_id);


--
-- Name: idx_42509_course_userss_user_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42509_course_userss_user_id_foreign ON public.course_users USING btree (user_id);


--
-- Name: idx_42514_course_users_user_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42514_course_users_user_id_foreign ON public.course_users_old USING btree (user_id);


--
-- Name: idx_42518_courses_program_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42518_courses_program_id_foreign ON public.courses USING btree (program_id);


--
-- Name: idx_42518_courses_scale_category_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42518_courses_scale_category_id_foreign ON public.courses USING btree (scale_category_id);


--
-- Name: idx_42518_courses_standard_category_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42518_courses_standard_category_id_foreign ON public.courses USING btree (standard_category_id);


--
-- Name: idx_42543_departments_faculty_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42543_departments_faculty_id_foreign ON public.departments USING btree (faculty_id);


--
-- Name: idx_42548_faculties_campus_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42548_faculties_campus_id_foreign ON public.faculties USING btree (campus_id);


--
-- Name: idx_42553_failed_jobs_uuid_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_42553_failed_jobs_uuid_unique ON public.failed_jobs USING btree (uuid);


--
-- Name: idx_42561_invites_email_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_42561_invites_email_unique ON public.invites USING btree (email);


--
-- Name: idx_42561_invites_invitation_token_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_42561_invites_invitation_token_unique ON public.invites USING btree (invitation_token);


--
-- Name: idx_42561_invites_user_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42561_invites_user_id_foreign ON public.invites USING btree (user_id);


--
-- Name: idx_42566_learning_activities_course_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42566_learning_activities_course_id_foreign ON public.learning_activities USING btree (course_id);


--
-- Name: idx_42572_learning_outcomes_course_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42572_learning_outcomes_course_id_foreign ON public.learning_outcomes USING btree (course_id);


--
-- Name: idx_42586_mapping_scale_programs_program_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42586_mapping_scale_programs_program_id_foreign ON public.mapping_scale_programs USING btree (program_id);


--
-- Name: idx_42590_mapping_scales_mapping_scale_categories_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42590_mapping_scales_mapping_scale_categories_id_foreign ON public.mapping_scales USING btree (mapping_scale_categories_id);


--
-- Name: idx_42602_okanagan_syllabi_syllabus_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42602_okanagan_syllabi_syllabus_id_foreign ON public.okanagan_syllabi USING btree (syllabus_id);


--
-- Name: idx_42609_vancovuer_syllabus_resources_id_name_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_42609_vancovuer_syllabus_resources_id_name_unique ON public.okanagan_syllabus_resources USING btree (id_name);


--
-- Name: idx_42614_optional_priorities_op_subdesc_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42614_optional_priorities_op_subdesc_foreign ON public.optional_priorities USING btree (op_subdesc);


--
-- Name: idx_42614_optional_priorities_subcat_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42614_optional_priorities_subcat_id_foreign ON public.optional_priorities USING btree (subcat_id);


--
-- Name: idx_42621_optional_priorities_course_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42621_optional_priorities_course_id_foreign ON public.optional_priorities_old USING btree (course_id);


--
-- Name: idx_42638_optional_priority_subcategories_cat_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42638_optional_priority_subcategories_cat_id_foreign ON public.optional_priority_subcategories USING btree (cat_id);


--
-- Name: idx_42644_outcome_activities_l_activity_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42644_outcome_activities_l_activity_id_foreign ON public.outcome_activities USING btree (l_activity_id);


--
-- Name: idx_42647_outcome_assessments_a_method_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42647_outcome_assessments_a_method_id_foreign ON public.outcome_assessments USING btree (a_method_id);


--
-- Name: idx_42650_outcome_maps_map_scale_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42650_outcome_maps_map_scale_id_foreign ON public.outcome_maps USING btree (map_scale_id);


--
-- Name: idx_42650_outcome_maps_pl_outcome_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42650_outcome_maps_pl_outcome_id_foreign ON public.outcome_maps USING btree (pl_outcome_id);


--
-- Name: idx_42655_p_l_o_categories_program_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42655_p_l_o_categories_program_id_foreign ON public.p_l_o_categories USING btree (program_id);


--
-- Name: idx_42659_password_resets_email_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42659_password_resets_email_index ON public.password_resets USING btree (email);


--
-- Name: idx_42663_program_learning_outcomes_plo_category_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42663_program_learning_outcomes_plo_category_id_foreign ON public.program_learning_outcomes USING btree (plo_category_id);


--
-- Name: idx_42663_program_learning_outcomes_program_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42663_program_learning_outcomes_program_id_foreign ON public.program_learning_outcomes USING btree (program_id);


--
-- Name: idx_42670_program_userss_program_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42670_program_userss_program_id_foreign ON public.program_users USING btree (program_id);


--
-- Name: idx_42670_program_userss_user_id_program_id_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_42670_program_userss_user_id_program_id_unique ON public.program_users USING btree (user_id, program_id);


--
-- Name: idx_42675_program_users_program_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42675_program_users_program_id_foreign ON public.program_users_old USING btree (program_id);


--
-- Name: idx_42686_role_user_user_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42686_role_user_user_id_foreign ON public.role_user USING btree (user_id);


--
-- Name: idx_42700_standard_scales_scale_category_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42700_standard_scales_scale_category_id_foreign ON public.standard_scales USING btree (scale_category_id);


--
-- Name: idx_42707_standards_standard_category_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42707_standards_standard_category_id_foreign ON public.standards USING btree (standard_category_id);


--
-- Name: idx_42714_standards_outcome_maps_course_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42714_standards_outcome_maps_course_id_foreign ON public.standards_outcome_maps USING btree (course_id);


--
-- Name: idx_42714_standards_outcome_maps_standard_scale_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42714_standards_outcome_maps_standard_scale_id_foreign ON public.standards_outcome_maps USING btree (standard_scale_id);


--
-- Name: idx_42726_syllabi_course_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42726_syllabi_course_id_foreign ON public.syllabi USING btree (course_id);


--
-- Name: idx_42735_syllabi_programs_program_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42735_syllabi_programs_program_id_foreign ON public.syllabi_programs USING btree (program_id);


--
-- Name: idx_42735_syllabi_programs_syllabus_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42735_syllabi_programs_syllabus_id_foreign ON public.syllabi_programs USING btree (syllabus_id);


--
-- Name: idx_42740_syllabi_resources_okanagan_o_syllabus_resource_id_for; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42740_syllabi_resources_okanagan_o_syllabus_resource_id_for ON public.syllabi_resources_okanagan USING btree (o_syllabus_resource_id);


--
-- Name: idx_42740_syllabi_resources_okanagan_syllabus_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42740_syllabi_resources_okanagan_syllabus_id_foreign ON public.syllabi_resources_okanagan USING btree (syllabus_id);


--
-- Name: idx_42745_syllabi_resources_vancouver_syllabus_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42745_syllabi_resources_vancouver_syllabus_id_foreign ON public.syllabi_resources_vancouver USING btree (syllabus_id);


--
-- Name: idx_42745_syllabi_resources_vancouver_v_syllabus_resource_id_fo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42745_syllabi_resources_vancouver_v_syllabus_resource_id_fo ON public.syllabi_resources_vancouver USING btree (v_syllabus_resource_id);


--
-- Name: idx_42750_syllabi_users_syllabus_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42750_syllabi_users_syllabus_id_foreign ON public.syllabi_users USING btree (syllabus_id);


--
-- Name: idx_42750_syllabi_users_user_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42750_syllabi_users_user_id_foreign ON public.syllabi_users USING btree (user_id);


--
-- Name: idx_42756_syllabus_instructors_syllabus_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42756_syllabus_instructors_syllabus_id_foreign ON public.syllabus_instructors USING btree (syllabus_id);


--
-- Name: idx_42761_users_email_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_42761_users_email_unique ON public.users USING btree (email);


--
-- Name: idx_42769_vancouver_syllabi_syllabus_id_foreign; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_42769_vancouver_syllabi_syllabus_id_foreign ON public.vancouver_syllabi USING btree (syllabus_id);


--
-- Name: idx_42776_vancovuer_syllabus_resources_id_name_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_42776_vancovuer_syllabus_resources_id_name_unique ON public.vancouver_syllabus_resources USING btree (id_name);


--
-- Name: assessment_methods assessment_methods_course_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assessment_methods
    ADD CONSTRAINT assessment_methods_course_id_foreign FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: course_optional_priorities course_optional_priorities_course_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_optional_priorities
    ADD CONSTRAINT course_optional_priorities_course_id_foreign FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: course_optional_priorities course_optional_priorities_op_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_optional_priorities
    ADD CONSTRAINT course_optional_priorities_op_id_foreign FOREIGN KEY (op_id) REFERENCES public.optional_priorities(op_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: course_programs course_programs_course_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_programs
    ADD CONSTRAINT course_programs_course_id_foreign FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: course_programs course_programs_program_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_programs
    ADD CONSTRAINT course_programs_program_id_foreign FOREIGN KEY (program_id) REFERENCES public.programs(program_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: course_schedules course_schedules_syllabus_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_schedules
    ADD CONSTRAINT course_schedules_syllabus_id_foreign FOREIGN KEY (syllabus_id) REFERENCES public.syllabi(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: course_users_old course_users_course_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_users_old
    ADD CONSTRAINT course_users_course_id_foreign FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: course_users_old course_users_user_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_users_old
    ADD CONSTRAINT course_users_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: course_users course_userss_course_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_users
    ADD CONSTRAINT course_userss_course_id_foreign FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: course_users course_userss_user_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_users
    ADD CONSTRAINT course_userss_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: courses courses_program_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_program_id_foreign FOREIGN KEY (program_id) REFERENCES public.programs(program_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: courses courses_scale_category_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_scale_category_id_foreign FOREIGN KEY (scale_category_id) REFERENCES public.standards_scale_categories(scale_category_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: courses courses_standard_category_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_standard_category_id_foreign FOREIGN KEY (standard_category_id) REFERENCES public.standard_categories(standard_category_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: departments departments_faculty_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_faculty_id_foreign FOREIGN KEY (faculty_id) REFERENCES public.faculties(faculty_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: faculties faculties_campus_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT faculties_campus_id_foreign FOREIGN KEY (campus_id) REFERENCES public.campuses(campus_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: invites invites_user_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invites
    ADD CONSTRAINT invites_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: learning_activities learning_activities_course_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learning_activities
    ADD CONSTRAINT learning_activities_course_id_foreign FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: learning_outcomes learning_outcomes_course_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learning_outcomes
    ADD CONSTRAINT learning_outcomes_course_id_foreign FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: mapping_scale_programs mapping_scale_programs_map_scale_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mapping_scale_programs
    ADD CONSTRAINT mapping_scale_programs_map_scale_id_foreign FOREIGN KEY (map_scale_id) REFERENCES public.mapping_scales(map_scale_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: mapping_scale_programs mapping_scale_programs_program_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mapping_scale_programs
    ADD CONSTRAINT mapping_scale_programs_program_id_foreign FOREIGN KEY (program_id) REFERENCES public.programs(program_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: mapping_scales mapping_scales_mapping_scale_categories_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mapping_scales
    ADD CONSTRAINT mapping_scales_mapping_scale_categories_id_foreign FOREIGN KEY (mapping_scale_categories_id) REFERENCES public.mapping_scale_categories(mapping_scale_categories_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: okanagan_syllabi okanagan_syllabi_syllabus_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.okanagan_syllabi
    ADD CONSTRAINT okanagan_syllabi_syllabus_id_foreign FOREIGN KEY (syllabus_id) REFERENCES public.syllabi(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: optional_priorities_old optional_priorities_course_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priorities_old
    ADD CONSTRAINT optional_priorities_course_id_foreign FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: optional_priorities optional_priorities_op_subdesc_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priorities
    ADD CONSTRAINT optional_priorities_op_subdesc_foreign FOREIGN KEY (op_subdesc) REFERENCES public.optional_priorities_subdescriptions(op_subdesc) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: optional_priorities optional_priorities_subcat_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priorities
    ADD CONSTRAINT optional_priorities_subcat_id_foreign FOREIGN KEY (subcat_id) REFERENCES public.optional_priority_subcategories(subcat_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: optional_priority_subcategories optional_priority_subcategories_cat_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optional_priority_subcategories
    ADD CONSTRAINT optional_priority_subcategories_cat_id_foreign FOREIGN KEY (cat_id) REFERENCES public.optional_priority_categories(cat_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: outcome_activities outcome_activities_l_activity_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outcome_activities
    ADD CONSTRAINT outcome_activities_l_activity_id_foreign FOREIGN KEY (l_activity_id) REFERENCES public.learning_activities(l_activity_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: outcome_activities outcome_activities_l_outcome_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outcome_activities
    ADD CONSTRAINT outcome_activities_l_outcome_id_foreign FOREIGN KEY (l_outcome_id) REFERENCES public.learning_outcomes(l_outcome_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: outcome_assessments outcome_assessments_a_method_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outcome_assessments
    ADD CONSTRAINT outcome_assessments_a_method_id_foreign FOREIGN KEY (a_method_id) REFERENCES public.assessment_methods(a_method_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: outcome_assessments outcome_assessments_l_outcome_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outcome_assessments
    ADD CONSTRAINT outcome_assessments_l_outcome_id_foreign FOREIGN KEY (l_outcome_id) REFERENCES public.learning_outcomes(l_outcome_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: outcome_maps outcome_maps_l_outcome_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outcome_maps
    ADD CONSTRAINT outcome_maps_l_outcome_id_foreign FOREIGN KEY (l_outcome_id) REFERENCES public.learning_outcomes(l_outcome_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: outcome_maps outcome_maps_map_scale_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outcome_maps
    ADD CONSTRAINT outcome_maps_map_scale_id_foreign FOREIGN KEY (map_scale_id) REFERENCES public.mapping_scales(map_scale_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: outcome_maps outcome_maps_pl_outcome_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outcome_maps
    ADD CONSTRAINT outcome_maps_pl_outcome_id_foreign FOREIGN KEY (pl_outcome_id) REFERENCES public.program_learning_outcomes(pl_outcome_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: p_l_o_categories p_l_o_categories_program_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.p_l_o_categories
    ADD CONSTRAINT p_l_o_categories_program_id_foreign FOREIGN KEY (program_id) REFERENCES public.programs(program_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: program_learning_outcomes program_learning_outcomes_plo_category_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_learning_outcomes
    ADD CONSTRAINT program_learning_outcomes_plo_category_id_foreign FOREIGN KEY (plo_category_id) REFERENCES public.p_l_o_categories(plo_category_id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: program_learning_outcomes program_learning_outcomes_program_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_learning_outcomes
    ADD CONSTRAINT program_learning_outcomes_program_id_foreign FOREIGN KEY (program_id) REFERENCES public.programs(program_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: program_users_old program_users_program_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_users_old
    ADD CONSTRAINT program_users_program_id_foreign FOREIGN KEY (program_id) REFERENCES public.programs(program_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: program_users_old program_users_user_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_users_old
    ADD CONSTRAINT program_users_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: program_users program_userss_program_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_users
    ADD CONSTRAINT program_userss_program_id_foreign FOREIGN KEY (program_id) REFERENCES public.programs(program_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: program_users program_userss_user_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.program_users
    ADD CONSTRAINT program_userss_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: role_user role_user_role_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_user
    ADD CONSTRAINT role_user_role_id_foreign FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: role_user role_user_user_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_user
    ADD CONSTRAINT role_user_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: standard_scales standard_scales_scale_category_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standard_scales
    ADD CONSTRAINT standard_scales_scale_category_id_foreign FOREIGN KEY (scale_category_id) REFERENCES public.standards_scale_categories(scale_category_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: standards_outcome_maps standards_outcome_maps_course_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standards_outcome_maps
    ADD CONSTRAINT standards_outcome_maps_course_id_foreign FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: standards_outcome_maps standards_outcome_maps_standard_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standards_outcome_maps
    ADD CONSTRAINT standards_outcome_maps_standard_id_foreign FOREIGN KEY (standard_id) REFERENCES public.standards(standard_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: standards_outcome_maps standards_outcome_maps_standard_scale_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standards_outcome_maps
    ADD CONSTRAINT standards_outcome_maps_standard_scale_id_foreign FOREIGN KEY (standard_scale_id) REFERENCES public.standard_scales(standard_scale_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: standards standards_standard_category_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standards
    ADD CONSTRAINT standards_standard_category_id_foreign FOREIGN KEY (standard_category_id) REFERENCES public.standard_categories(standard_category_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: syllabi syllabi_course_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi
    ADD CONSTRAINT syllabi_course_id_foreign FOREIGN KEY (course_id) REFERENCES public.courses(course_id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: syllabi_programs syllabi_programs_program_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_programs
    ADD CONSTRAINT syllabi_programs_program_id_foreign FOREIGN KEY (program_id) REFERENCES public.programs(program_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: syllabi_programs syllabi_programs_syllabus_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_programs
    ADD CONSTRAINT syllabi_programs_syllabus_id_foreign FOREIGN KEY (syllabus_id) REFERENCES public.syllabi(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: syllabi_resources_okanagan syllabi_resources_okanagan_o_syllabus_resource_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_resources_okanagan
    ADD CONSTRAINT syllabi_resources_okanagan_o_syllabus_resource_id_foreign FOREIGN KEY (o_syllabus_resource_id) REFERENCES public.okanagan_syllabus_resources(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: syllabi_resources_okanagan syllabi_resources_okanagan_syllabus_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_resources_okanagan
    ADD CONSTRAINT syllabi_resources_okanagan_syllabus_id_foreign FOREIGN KEY (syllabus_id) REFERENCES public.syllabi(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: syllabi_resources_vancouver syllabi_resources_vancouver_syllabus_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_resources_vancouver
    ADD CONSTRAINT syllabi_resources_vancouver_syllabus_id_foreign FOREIGN KEY (syllabus_id) REFERENCES public.syllabi(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: syllabi_resources_vancouver syllabi_resources_vancouver_v_syllabus_resource_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_resources_vancouver
    ADD CONSTRAINT syllabi_resources_vancouver_v_syllabus_resource_id_foreign FOREIGN KEY (v_syllabus_resource_id) REFERENCES public.vancouver_syllabus_resources(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: syllabi_users syllabi_users_syllabus_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_users
    ADD CONSTRAINT syllabi_users_syllabus_id_foreign FOREIGN KEY (syllabus_id) REFERENCES public.syllabi(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: syllabi_users syllabi_users_user_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabi_users
    ADD CONSTRAINT syllabi_users_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: syllabus_instructors syllabus_instructors_syllabus_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.syllabus_instructors
    ADD CONSTRAINT syllabus_instructors_syllabus_id_foreign FOREIGN KEY (syllabus_id) REFERENCES public.syllabi(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: vancouver_syllabi vancouver_syllabi_syllabus_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vancouver_syllabi
    ADD CONSTRAINT vancouver_syllabi_syllabus_id_foreign FOREIGN KEY (syllabus_id) REFERENCES public.syllabi(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.migrations (id, migration, batch) FROM stdin;
57	2014_10_12_000000_create_users_table	1
58	2014_10_12_100000_create_password_resets_table	1
59	2019_08_19_000000_create_failed_jobs_table	1
60	2020_09_30_230930_create_programs_table	1
61	2020_10_01_015240_create_courses_table	1
62	2020_10_01_040348_create_learning_outcomes_table	1
63	2020_10_01_045146_create_learning_activities_table	1
64	2020_10_01_050955_create_assessment_methods_table	1
65	2020_10_02_044053_create_roles_table	1
66	2020_10_02_044814_create_role_user_table	1
67	2020_10_04_112114_create_course_users_table	1
68	2020_10_12_033720_create_program_users_table	1
69	2020_10_12_040046_create_p_l_o_categories_table	1
70	2020_10_12_063957_create_program_learning_outcomes_table	1
71	2020_10_16_030821_create_outcome_assessments_table	1
72	2020_10_16_030926_create_outcome_activities_table	1
73	2020_10_23_193349_create_outcome_maps_table	1
74	2020_11_06_213928_create_mapping_scales_table	1
75	2020_11_18_201559_create_mapping_scale_programs_table	1
76	2021_02_12_172212_update_courses_table	1
77	2021_02_24_185203_create_custom_learning_activities_table	1
78	2021_02_26_184047_create_custom_assessment_methods_table	1
79	2021_03_05_180845_create_invites_table	1
80	2021_03_25_204559_create_optional_program_learning_outcomes_table	1
81	2021_04_27_172715_create_optional_priorities_table	1
82	2021_06_04_174755_create_syllabi_table	1
94	2021_06_15_205336_create_course_programs_table	2
95	2021_06_16_224720_update_program_courses_table	3
96	2021_06_28_204736_create_standards_scale_categories_table	4
97	2021_06_28_205119_create_standard_scales_table	5
98	2021_06_28_205601_create_standard_categories_table	6
99	2021_06_28_205904_create_standards_table	7
100	2021_06_28_210155_create_standards_outcome_maps_table	8
101	2021_06_22_203247_update_m_s_courses	9
102	2021_07_02_220532_create_mapping_scale_categories_table	10
103	2021_07_02_221302_update_mapping_scale	11
106	2021_07_12_151933_update_syllabi_and_syllabi_users_tables	12
107	2021_07_12_154153_create_syllabus_tables	12
108	2021_07_26_120458_add_map_scale_id_column	13
109	2021_07_28_141437_standards_use_map_scale_id	14
111	2021_08_03_091358_add_notes_course_programs	15
112	2021_08_04_125452_update_course_users	16
113	2021_08_09_095100_update_program_users	17
114	2021_06_23_182042_create_optional_priority_categories_table	18
115	2021_06_24_181949_create_optional_priority_subcategories_table	18
116	2021_06_25_172715_create_optional_priorities_table	18
117	2021_06_26_181737_create_course_optional_priorities_table	18
118	2021_08_26_133944_update_optional_priorities_table	19
119	2021_10_15_102536_create_course_schedules_table	19
120	2021_10_19_142345_add_is_checkable_optional_priority	19
121	2021_11_09_150019_add_last_modified_user_to_tables	19
122	2021_11_17_003638_update_learning_outcomes_table	19
123	2021_12_22_145255_create_campuses_table	19
124	2021_12_22_145920_create_faculties_table	19
125	2021_12_22_150430_create_departments_table	19
126	2022_01_05_110323_update_programs_table	19
127	2022_01_25_113651_add_has_temp_password_to_users_table	19
128	2022_02_28_143658_make_course_num_nullable	19
129	2022_04_11_154306_update_class_meeting_days_syllabi_table	19
130	2022_05_11_121741_create_optional_priorities_subdescriptions_table	19
131	2022_05_11_122210_add_subdescriptions_to_optional_priorities_table	19
132	2022_05_19_120217_add_delivery_modality_to_syllabi_table	19
133	2022_05_25_143318_update_assessment_methods_table	19
134	2022_06_01_181506_add_l_activities_pos_to_learning_activities_table	19
135	2022_06_20_005833_create_syllabus_instructors_table	19
136	2022_06_28_132955_add_course_id_to_standards_outcome_maps_table	19
137	2022_07_03_214954_update_syllabi_table	19
138	2022_07_11_144058_create_syllabi_programs_table	19
139	2022_07_29_151317_update_okanagan__syllabi	19
140	2023_02_17_155758_add_copyirght_to_syllabi_table	19
141	2023_02_18_101938_add_land_acknow_to_syllabi	19
142	2023_02_22_131211_add_custom_resource_to_syllabi_table	19
143	2023_06_23_150815_add_cross_listedto_syllabi_table	19
144	2023_06_23_150815_add_prereq_coreqs_to_syllabi_table	19
\.


--
-- Name: migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.migrations_id_seq', 144, true);


--
-- PostgreSQL database dump complete
--

