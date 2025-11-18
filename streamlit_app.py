import streamlit as st
import logging

# Try importing clips (if unavailable, notify in the UI)
try:
    import clips
    CLIPS_AVAILABLE = True
except Exception as _e:
    clips = None
    CLIPS_AVAILABLE = False


logging.basicConfig(level=logging.INFO, format="%(message)s")


def create_env():
    """Create and return a CLIPS environment (if available)."""
    env = clips.Environment()
    # LoggingRouter is available in some CLIPS bindings to capture CLIPS logs
    try:
        router = clips.LoggingRouter()
        env.add_router(router)
    except Exception:
        # If LoggingRouter does not exist, ignore it. It does not affect basic inference.
        pass
    return env


st.title("Expert System LAB 2")

st.write("This demo will take your input, assert it as a fact into CLIPS, run inference, and display the result.")

name = st.text_input("Enter your name")

if st.button("Run inference"):
    if not CLIPS_AVAILABLE:
        st.error("Failed to import 'clips' module. Please install it (e.g., pip install clips or install the proper bindings for your environment).")
    else:
        # Create the environment and define a simple template
        env = create_env()

        # Define a template to store results (only contains one slot: name)
        env.build('(deftemplate result (slot name))')

        # Assert a fact into working memory.
        # Use double quotes to ensure names with spaces work.
        if name and name.strip():
            fact_str = f'(result (name "{name}"))'
        else:
            fact_str = '(result (name "<no-name>"))'

        # assert_string is used to assert fact text into CLIPS
        try:
            env.assert_string(fact_str)
        except Exception as e:
            st.error(f"Failed to assert fact: {e}")
            raise

        # Run the inference engine
        try:
            env.run()
        except Exception as e:
            st.error(f"CLIPS execution failed: {e}")
            raise

        # Collect results
        results = []
        try:
            for fact in env.facts():
                # Only collect facts with template name 'result'
                try:
                    template_name = fact.template.name
                except Exception:
                    # Skip invalid fact objects
                    continue

                if template_name == 'result':
                    # Try multiple access methods for compatibility
                    value = None
                    try:
                        value = fact['name']
                    except Exception:
                        try:
                            # Some implementations use attribute access
                            value = getattr(fact, 'name', None)
                        except Exception:
                            value = None

                    # Convert iterable/multivalue to string
                    if value is None:
                        results.append(str(fact))
                    else:
                        results.append(str(value))
        except Exception as e:
            st.error(f"Failed to read facts: {e}")

        if results:
            st.success(f"Result: {results[0]}")
        else:
            st.info("No results found.")
