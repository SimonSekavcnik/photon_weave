from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple, Union, Callable, Optional

import jax
import jax.numpy as jnp

import photon_weave.extra.einsum_constructor as ESC
from photon_weave.photon_weave import Config

if TYPE_CHECKING:
    from photon_weave.state.base_state import BaseState


def measure_vector(
    state_objs: Union[List[BaseState], Tuple[BaseState, ...]],
    target_states: Union[List[BaseState], Tuple[BaseState, ...]],
    product_state: jnp.ndarray,
    prob_callback: Optional[Callable[[BaseState, jnp.ndarray], None]] = None
) -> Tuple[Dict[BaseState, int], jnp.ndarray]:
    """
    Measures state vector and returns the outcome with the
    post measurement state.

    Parameters
    ----------
    state_objs:Union[List[BaseState],Tuple[BaseState, ...]]
        List of all state objects which are in the probuct state
    target_states: Union[List[BaseState],Tuple[BaseState, ...]]
        List of the states, which should be measured
    product_state: jnp.ndarray
        Product state containing the states to be measured
    prob_callback: Optional[Callable[[BaseState, jnp.ndarray],None]]
        Probability callback, used for testing the correctness of
        measurement outcome probabilities

    Returns
    -------
    Tuple[Dict[BaseState, int], jnp.ndarray]
        A Tuple containing:
        - A dictionary mapping each target state to its measurement
        - A jax array representing the post measuremen state of the rest of the
          product state

    Notes:
    ------
    calls the prob_callback() if provided
    """
    state_objs = list(state_objs)
    assert isinstance(product_state, jnp.ndarray), \
        f"Expected jnp.ndarray, received {type(product_state)}"
    expected_dims = jnp.prod(jnp.array([s.dimensions for s in state_objs]))
    assert product_state.shape == (expected_dims, 1), \
       f"Expected shape: ({expected_dims},1) , Received shape {product_state.shape}"

    # Reshape the array into the tensor
    shape = [s.dimensions for s in state_objs]
    shape.append(1)
    product_state = product_state.reshape(shape)

    C = Config()
    outcomes = {}
    for idx, state in enumerate(target_states):
        probabilities = []
        dims = state.dimensions
        for moutcome in range(dims):
            slicer = [slice(None)] * len(product_state.shape)
            slicer[state_objs.index(state)] = moutcome
            slice_psi = product_state[tuple(slicer)]
            probabilities.append(
                jnp.sum(jnp.abs(slice_psi)**2)
                )
        probabilities = jnp.array(probabilities)
        probabilities /= jnp.sum(probabilities)

        # For testing correctness of measurement probabilities
        if prob_callback:
            prob_callback(state, probabilities)

        # Based on the probabilities and key we choose outcome
        key = C.random_key
        outcome = jax.random.choice(
            key, a=jnp.arange(state.dimensions), p=probabilities
        )
        outcomes[state] = int(outcome)

        # We remove the measured system from the product state
        indices: List[Union[slice, int]] = [slice(None)] * len(product_state.shape)
        indices[state_objs.index(state)] = outcomes[state]
        product_state = product_state[tuple(indices)]

        state_objs.remove(state)

    product_state = product_state.reshape(-1, 1)

    return outcomes, product_state


def measure_matrix(
    state_objs: Union[List[BaseState], Tuple[BaseState, ...]],
    target_states: Union[List[BaseState], Tuple[BaseState, ...]],
    product_state: jnp.ndarray,
    prob_callback: Optional[Callable[[BaseState, jnp.ndarray], None]] = None
) -> Tuple[Dict[BaseState, int], jnp.ndarray]:
    """
    Measures Density Matrix and returns the outcome with the
    post measurement state of the product states, which were not measured.

    Parameters
    ----------
    state_objs: List[BaseState]
        List of all state objects which are in the probuct state
    target_states: List[BaseState]
        List of the states, which should be measured
    product_state: jnp.ndarray
        Product state containing the states to be measured
    prob_callback: Optional[Callable[[BaseState, jnp.ndarray],None]]
        Probability callback, used for testing the correctness of
        measurement outcome probabilities

    Returns
    -------
    Tuple[Dict[BaseState, int], jnp.ndarray]
        A Tuple containing:
        - A dictionary mapping each target state to its measurement
        - A jax array representing the post measuremen state of the rest of the
          product state

    Notes:
    ------
    calls the prob_callback() if provided
    """
    state_objs = list(state_objs)

    assert isinstance(product_state, jnp.ndarray), \
        f"Expected jnp.ndarray, received {type(product_state)}"
    expected_dims = jnp.prod(jnp.array([s.dimensions for s in state_objs]))
    assert product_state.shape == (expected_dims, expected_dims), \
       f"Expected shape: ({expected_dims},{expected_dims}) , Received shape {product_state.shape}"

    # Reshape the array into the tensor
    shape = [s.dimensions for s in state_objs] * 2
    product_state = product_state.reshape(shape)

    C = Config()
    outcomes = {}
    for idx, state in enumerate(target_states):
        probabilities = []
        dims = state.dimensions
        state_index = state_objs.index(state)
        for moutcome in range(dims):
            slicer = [slice(None)] * len(product_state.shape)
            slicer[state_index] = moutcome
            slicer[state_index + len(state_objs)] = moutcome
            block = product_state[tuple(slicer)]
            block = block.reshape((int(block.size//block.size**0.5), -1))
            probabilities.append(
                float(jnp.real(jnp.trace(block)))
            )

        #probabilities = jnp.abs(jnp.diag(projected_state))
        probabilities = jnp.array(probabilities)
        probabilities /= jnp.sum(probabilities)
        # For testing correctness of measurement probabilities
        if prob_callback:
            prob_callback(state, probabilities)

        # Based on the probabilities and key we choose outcome
        key = C.random_key
        outcome = jax.random.choice(
            key, a=jnp.arange(state.dimensions), p=probabilities
        )
        outcomes[state] = int(outcome)

        # Construct post measurement state
        state_index = state_objs.index(state)
        row_idx = state_index
        col_idx = state_index + len(state_objs)
        indices = [slice(None)] * len(product_state.shape)
        indices[row_idx] = outcomes[state]  # type: ignore
        indices[col_idx] = outcomes[state]  # type: ignore
        product_state = product_state[tuple(indices)]

        state_objs.remove(state)

    if len(state_objs) > 0:
        new_dims = jnp.prod(jnp.array([s.dimensions for s in state_objs]))
        product_state = product_state.reshape((new_dims, new_dims))

    return outcomes, product_state


def measure_POVM_matrix(
    state_objs: Union[List[BaseState], Tuple[BaseState, ...]],
    target_states: Union[List[BaseState], Tuple[BaseState, ...]],
    operators: Union[List[jnp.ndarray], Tuple[jnp.ndarray]],
    product_state: jnp.ndarray,
) -> Tuple[int, jnp.ndarray]:
    """
    Peform POVM measurement on the given product state.

    Parameters
    ----------
    state_objs: List[BaseState]
        List of BaseState objects included in the product stats
    target_states: List[BaseState]
        List of the stater in the product state, which will
        be measured with given operators
    operators: List[jnp.ndarray]
        list of the POVM operators, which desctibe the POVM measurement.
        The operators need to have correct dimensionality.
    product_state: jnp.ndarray
        The product state on which the measurement will be performed

    Returns
    -------
    Tuple[int, jnp.ndarray]
        Returns tuple with the index of the measurement outcome, where
        index refers to the index of the operator given in the operators
        list and the post measurement state

    Notes
    -----
    The states need to be tensored in the correct order. This is handled
    by the Photon Weave by default. In case of using this function
    specifically, make sure to have the states correctly ordered.
    """

    state_objs = list(state_objs)
    target_states = list(target_states)
    # Transform the operators to tensors
    op_shape = [s.dimensions for s in target_states] * 2
    operators = [op.reshape(op_shape) for op in operators]
    product_state = product_state.reshape([s.dimensions for s in state_objs] * 2)
    target_dims = jnp.prod(jnp.array([s.dimensions for s in target_states]))

    einsum_op = ESC.apply_operator_matrix(state_objs, target_states)
    einsum_to = ESC.trace_out_matrix(state_objs, target_states)
    prob_list: List[float] = []

    # Get the dimensions
    for operator in operators:
        projected_state = jnp.einsum(
            einsum_op, operator, product_state, jnp.conj(operator)
        )

        traced_out_projected_state = jnp.einsum(einsum_to, projected_state).reshape(
            (target_dims, target_dims)
        )

        prob_list.append(float(jnp.trace(traced_out_projected_state).real))

    probabilities = jnp.array(prob_list)
    probabilities /= jnp.sum(probabilities)

    C = Config()
    key = C.random_key
    outcome = int(jax.random.choice(key, a=jnp.arange(len(operators)), p=probabilities))
    product_state = jnp.einsum(
        einsum_op, operators[outcome], product_state, jnp.conj(operators[outcome])
    )

    product_state /= jnp.linalg.norm(product_state)

    state_dims = jnp.prod(jnp.array([s.dimensions for s in state_objs]))
    product_state = product_state.reshape((state_dims, state_dims))
    return outcome, product_state
